from .auth import auth_route
from .meet import meet_route
from .create_meet import create_meet_route
from .profile import profile_route

routes = [
    auth_route,
    meet_route,
    create_meet_route,
    profile_route,
]

