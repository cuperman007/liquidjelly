-- Pages has no Cron Triggers. Expired records are pruned when a new enquiry arrives.
CREATE TRIGGER prune_expired_enquiries AFTER INSERT ON enquiries
BEGIN
  DELETE FROM enquiries
  WHERE created_at < strftime('%Y-%m-%dT%H:%M:%fZ','now','-12 months');
END;
