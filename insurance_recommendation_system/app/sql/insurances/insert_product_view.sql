INSERT INTO product_view_history (user_id, product_id, last_time_viewed_at, views_count)
VALUES (%(user_id)s, %(product_id)s, CURRENT_TIMESTAMP, 1)
ON CONFLICT (user_id, product_id)
DO UPDATE SET
    last_time_viewed_at = EXCLUDED.last_time_viewed_at,
    views_count = product_view_history.views_count + 1;
