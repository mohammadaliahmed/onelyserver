# HelpHub API
[url] - adresa na kojoj se nalazi api, treba da se cuva u strings.xml (lokalno je 127.0.0.1:5000)
Ukoliko request u imenu ima * znaci da zahteva token, kao bearer token staviti token

[url[ - address where the API is stored. You have the url in swift project I sent you, please try to find it. If the request in its name has "*", that means the request needs bearer token. 

## Standardni objekti
Lista objekata:
sadrzi i parametre page i per_page primer: [url]/api/users/nikola?page=2&per_page=10
{
    'items': [item.to_dict() for item in resources.items],
    '_meta': {
        'page': page,
        'per_page': per_page,
        'total_pages': resources.pages,
        'total_items': resources.total
    },
    '_links': {
        'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
        'next': url_for(endpoint, page=page + 1, per_page=per_page, **kwargs) if resources.has_next else None,
        'prev': url_for(endpoint, page=page - 1, per_page=per_page, **kwargs) if resources.has_prev else None
    }
}

User:
{
    'id': self.id,
    'username': self.username,
    'last_seen': self.last_seen.isoformat() + 'Z',
    'about_me': self.about_me,
    'email': self.email, -opciono, ako je tvoj profil onda ide-
    '_links': {
        'self': url_for('api.get_user', id=self.id),
        'avatar': self.avatar
    }
}

## User Management
1. Registracija
POST na [url]/api/users
Body: {"username": -username-, "email":-email-, "password":-password-}
Response: Registrovani User

1. Registration
POST to [url]/api/users
Body: {"username": -username-, "email":-email-, "password":-password-}
Response: Registered User

2. Login
POST na [url]/api/tokens
Basic Auth sadrzi username i password
Response: {"token": -token-}
Token istice posle 1h

2. Login
POST to [url]/api/tokens
Basic Auth contains username and password
Response: {"token": -token-}
Token expires after 1h

3. *Logout
DELETE na [url]/api/tokens
Response: prazno, kod 204
Invalidira token

3. *Logout
DELETE to [url]/api/tokens
Response: empty, code 204
It will invalidate the token

4. *Podaci o sebi
GET na [url]/api/users
Response: svoj User sa emailom

4. *Data about user
GET na [url]/api/users
Response: user data

5. *Podaci o nekom korisniku
GET to [url]/api/users/<id> - id trazenog korisnika 
Response: trazeni User
    
5. *Data about some user
GET on [url]/api/users/<id> - id of searched person
Response: searched user

6. *Azuriranje podataka o sebi
PUT na [url]/api/users
Body: kombinacija parametara username, email, about_me, avatar
Response: svoj User

6. *Updating your data
PUT to [url]/api/users
Body: combination of parameters username, email, about_me, avatar
Response: user

7. *Pretraga korisnika
GET na [URL]/api/users/<search_term> - search_term je pocetak imena
Response: Lista User
Radi pretragu korisnika po principu Like "<search_term>*"

7. *Search for user
GET to [URL]/api/users/<search_term> - search_term is the start of the name(John - Jo will be the search term for example)
Response: List of users
Search works Like "<search_term>*"

## Followers
1. *Followers
GET na [url]/followers
Response: Lista User

1. *Followers
GET to [url]/followers
Response: list of users

2. *Following
GET na [url]/following
Response: Lista User

2. *Following
GET to [url]/following
Response: List of Users

3. *Provera da li prati korisnika
GET na [url]/following/<id>
Response {'following': true/false}
    
3. *Checking if user is following other user with id
GET to [url]/following/<id>
Response {'following': true/false}

4. Zapracivanje
GET na [url]/follow/<id>
Response: User koji je zapracen
    
4. Following
GET to [url]/follow/<id>
Response: User who is followed

5. Otpracivanje
GET na [url]/unfollow/<id>
Response: User koji je otpracen
    
5. Unfollowing
GET to [url]/unfollow/<id>
Response: user who is unfollowed
#   o n e l y s e r v e r  
 #   o n e l y s e r v e r  
 