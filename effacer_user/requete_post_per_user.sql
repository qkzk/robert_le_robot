select id from posts where userid = (SELECT id FROM users WHERE username ='qkzk');
