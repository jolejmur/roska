import requests
import json

# Base URL
BASE_URL = "http://localhost:8000/api"

print("=== Test API de Usuarios ===\n")

# 1. Login
print("1. Intentando login como admin...")
login_data = {
    "email": "admin@roska.com",
    "password": "admin123"
}

try:
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")

    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access')
        print(f"✓ Login exitoso! Token obtenido.")

        # 2. Listar usuarios
        print("\n2. Intentando listar usuarios...")
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(f"{BASE_URL}/users/", headers=headers)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            users_data = response.json()
            print(f"Response: {json.dumps(users_data, indent=2)[:500]}")

            if isinstance(users_data, dict) and 'results' in users_data:
                print(f"✓ Total usuarios: {users_data.get('count', 0)}")
                print(f"✓ Usuarios en esta página: {len(users_data.get('results', []))}")
            elif isinstance(users_data, list):
                print(f"✓ Total usuarios: {len(users_data)}")
        else:
            print(f"✗ Error al listar usuarios")
            print(f"Response: {response.text[:500]}")
    else:
        print(f"✗ Error en login")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"✗ Error: {e}")

print("\n=== Fin del Test ===")
