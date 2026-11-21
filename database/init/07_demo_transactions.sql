-- Existing development databases can apply this file once as the database admin.
ALTER TABLE transactions
    ADD COLUMN is_demo BOOLEAN NOT NULL DEFAULT FALSE,
    DROP CONSTRAINT transaction_one_actor,
    ADD CONSTRAINT transaction_one_actor CHECK (
        num_nonnulls(customer_id, employee_id) = CASE WHEN is_demo THEN 0 ELSE 1 END
    );
