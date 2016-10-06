/*
 * Custom SQL that is executed just after the CREATE TABLE statements when you
 * run syncdb.
 * Will use this to add in the configurations that are expected by ejabberd's
 * `rosterusers` table schema
 */

ALTER TABLE ONLY rosterusers ALTER COLUMN created_at SET DEFAULT now();

-- these constraints come right out of ejabberd's pg.sql
-- https://github.com/processone/ejabberd/blob/master/sql/pg.sql
CREATE UNIQUE INDEX i_rosteru_user_jid ON rosterusers USING btree (username, jid);
CREATE INDEX i_rosteru_username ON rosterusers USING btree (username);
CREATE INDEX i_rosteru_jid ON rosterusers USING btree (jid);