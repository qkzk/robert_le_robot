-- effacer les posts "soft delete"
DELETE FROM posts WHERE deleteat > 0;

-- effacer les posts "plus vieux que... attention, il faut fournir un unix timestamp en ms (typiquement 1000 * python.unix.timestamp)"
DELETE FROM posts WHERE createat < x;
