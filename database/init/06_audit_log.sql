--Audit log for employees, customers, accounts, transactions
CREATE TABLE audit_logs (
    log_id        BIGSERIAL    PRIMARY KEY,
    table_name    VARCHAR(50)  NOT NULL,
    operation     VARCHAR(10)  NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    record_id     BIGINT,                    -- primary key of the affected row
    old_data      JSONB,                     -- NULL for INSERT
    new_data      JSONB,                     -- NULL for DELETE
    app_role      VARCHAR(20),               -- app.current_role session var
    employee_id   BIGINT,                    -- app.current_employee_id session var
    customer_id   BIGINT,                    -- app.current_customer_id session var
    db_user       TEXT NOT NULL DEFAULT current_user,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_table_name  ON audit_logs (table_name);
CREATE INDEX idx_audit_record_id   ON audit_logs (table_name, record_id);
CREATE INDEX idx_audit_created_at  ON audit_logs (created_at);


CREATE OR REPLACE FUNCTION fn_audit_log()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER   -- runs as the function owner (superuser), so it can always write to logs
SET search_path = public
AS $$
DECLARE
    v_record_id  BIGINT;
    v_old_data   JSONB;
    v_new_data   JSONB;
    v_role       TEXT;
    v_emp_id     BIGINT;
    v_cust_id    BIGINT;
BEGIN
    -- Read application session variables (empty string → NULL)
    v_role    := NULLIF(current_setting('app.current_role',        true), '');
    v_emp_id  := NULLIF(current_setting('app.current_employee_id', true), '')::BIGINT;
    v_cust_id := NULLIF(current_setting('app.current_customer_id', true), '')::BIGINT;

    IF TG_OP = 'INSERT' THEN
        v_new_data  := to_jsonb(NEW);
        v_old_data  := NULL;
        -- Derive the primary key from the new row's first column by convention;
        EXECUTE format('SELECT ($1).%I::BIGINT', TG_ARGV[0]) INTO v_record_id USING NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        v_old_data  := to_jsonb(OLD);
        v_new_data  := to_jsonb(NEW);
        EXECUTE format('SELECT ($1).%I::BIGINT', TG_ARGV[0]) INTO v_record_id USING NEW;

    ELSIF TG_OP = 'DELETE' THEN
        v_old_data  := to_jsonb(OLD);
        v_new_data  := NULL;
        EXECUTE format('SELECT ($1).%I::BIGINT', TG_ARGV[0]) INTO v_record_id USING OLD;
    END IF;

    -- Remove password_hash from captured data to avoid storing credentials
    v_old_data := v_old_data - 'password_hash';
    v_new_data := v_new_data - 'password_hash';

    INSERT INTO audit_logs
        (table_name, operation, record_id, old_data, new_data,
         app_role, employee_id, customer_id)
    VALUES
        (TG_TABLE_NAME, TG_OP, v_record_id, v_old_data, v_new_data,
         v_role, v_emp_id, v_cust_id);

    RETURN NULL;
END;
$$;


-- Attach triggers to every sensitive table
CREATE TRIGGER audit_employees
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH ROW EXECUTE FUNCTION fn_audit_log('employee_id');

CREATE TRIGGER audit_customers
    AFTER INSERT OR UPDATE OR DELETE ON customers
    FOR EACH ROW EXECUTE FUNCTION fn_audit_log('customer_id');

CREATE TRIGGER audit_accounts
    AFTER INSERT OR UPDATE OR DELETE ON accounts
    FOR EACH ROW EXECUTE FUNCTION fn_audit_log('account_id');

CREATE TRIGGER audit_transactions
    AFTER INSERT OR UPDATE OR DELETE ON transactions
    FOR EACH ROW EXECUTE FUNCTION fn_audit_log('transaction_id');


-- Permissions — append-only for the application role - only INSERT and SELECT for display/reporting 
-- UPDATE and DELETE are withheld so logs cannot be erased
GRANT SELECT, INSERT ON audit_logs TO banking_app;
GRANT USAGE, SELECT  ON SEQUENCE audit_logs_log_id_seq TO banking_app;

