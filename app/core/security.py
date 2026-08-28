# app/core/security.py

# Esta es una versión para hacer pruebas sin que nos pida contraseña
def get_current_user():
    # Simulamos que un operario está usando la app
    return {"employee_code": "OP-001", "role": "Worker"}