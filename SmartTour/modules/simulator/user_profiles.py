# user_profiles.py
# Perfiles de usuario sintéticos o reales para simulación

# Aquí puedes definir las clases, funciones y datos necesarios
# para crear y manejar perfiles de usuario en tu aplicación.

class UserProfile:
    def __init__(self, username, email, is_real=True):
        self.username = username
        self.email = email
        self.is_real = is_real

    def __repr__(self):
        return f"UserProfile(username={self.username}, email={self.email}, is_real={self.is_real})"

# Funciones para crear perfiles de usuario sintéticos o reales
def create_real_user_profile(username, email):
    return UserProfile(username, email, is_real=True)

def create_synthetic_user_profile(username):
    # El email sintético podría generarse de alguna manera específica
    email = f"{username}@example.com"
    return UserProfile(username, email, is_real=False)