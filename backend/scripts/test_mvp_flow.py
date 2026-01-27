import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000/api/v1"
PROJECT_ID = 1

def run_mvp_flow():
    print("🚀 Iniciando Test de Flujo MVP con Identidad 'Analista Tech'...")

    # 1. Buscar la identidad "Analista Tech" y actualizarla si es necesario
    print("\n1. Buscando identidad 'Analista Tech'...")
    try:
        res = requests.get(f"{BASE_URL}/identities/?project_id={PROJECT_ID}")
        res.raise_for_status()
        identities = res.json()
        
        target_identity = None
        for identity in identities:
            if identity['name'] == "Analista Tech":
                target_identity = identity
                break
        
        if not target_identity:
            print("❌ No se encontró la identidad 'Analista Tech'. Creándola...")
            # Create it if missing
            create_payload = {
                "name": "Analista Tech",
                "purpose": "Explicar tecnología compleja de forma simple",
                "tone": "Técnico y directo",
                "preferred_platforms": ["LinkedIn", "Twitter"],
                "communication_style": "Directo y técnico",
                "content_limits": "No usar emojis, no usar jerga de marketing",
                "status": "active"
            }
            res = requests.post(f"{BASE_URL}/identities/?project_id={PROJECT_ID}", json=create_payload)
            res.raise_for_status()
            target_identity = res.json()
            print(f"✅ Identidad Creada: {target_identity['name']} (ID: {target_identity['id']})")
        else:
            print(f"✅ Identidad Encontrada: {target_identity['name']} (ID: {target_identity['id']})")
            
            # Update if fields are missing
            needs_update = False
            update_payload = {}
            
            if not target_identity.get('communication_style'):
                update_payload['communication_style'] = "Directo y técnico"
                needs_update = True
            if not target_identity.get('content_limits'):
                update_payload['content_limits'] = "No usar emojis, no usar jerga de marketing"
                needs_update = True
                
            if needs_update:
                print("🔄 Actualizando identidad con campos faltantes (MVP PRO)...")
                res = requests.put(f"{BASE_URL}/identities/{target_identity['id']}", json=update_payload)
                res.raise_for_status()
                target_identity = res.json() # Refresh
                print("✅ Identidad Actualizada.")

        print(f"   - Tono: {target_identity['tone']}")
        print(f"   - Estilo: {target_identity.get('communication_style')}")
        print(f"   - Límites: {target_identity.get('content_limits')}")

    except Exception as e:
        print(f"❌ Error buscando/actualizando identidad: {e}")
        return

    # 2. Crear Campaña de Prueba
    print("\n2. Creando campaña de prueba vinculada...")
    campaign_payload = {
        "project_id": PROJECT_ID,
        "name": f"Demo Tech Campaign {int(time.time())}",
        "objective": "Explicar cómo funciona una API REST a principiantes",
        "tone": "Educational", 
        "identity_id": target_identity['id'],
        "status": "active",
        "start_date": "2026-01-27"
    }

    try:
        res = requests.post(f"{BASE_URL}/campaigns/", json=campaign_payload)
        res.raise_for_status()
        campaign = res.json()
        campaign_id = campaign['id']
        print(f"✅ Campaña Creada: '{campaign['name']}' (ID: {campaign_id})")
    except Exception as e:
        print(f"❌ Error creando campaña: {e}")
        return

    # 3. Generar Post usando IA
    print("\n3. Generando post con IA (aplicando identidad)...")
    generate_payload = {
        "count": 1,
        "platform": "linkedin"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/campaigns/{campaign_id}/generate", json=generate_payload)
        res.raise_for_status()
        gen_data = res.json()
        print(f"✅ Generación completada. Posts generados: {gen_data.get('generated_count')}")
    except Exception as e:
        print(f"❌ Error en generación IA: {e}")
        return

    # 4. Leer el Post Generado
    print("\n4. Leyendo el contenido generado para verificar tono y límites...")
    try:
        res = requests.get(f"{BASE_URL}/posts/?project_id={PROJECT_ID}") 
        res.raise_for_status()
        response_data = res.json()
        
        # Handle wrapped response if applicable
        all_posts = response_data.get('data') if isinstance(response_data, dict) and 'data' in response_data else response_data
        
        if not isinstance(all_posts, list):
             print(f"⚠️ Formato de respuesta inesperado: {type(all_posts)}")
             print(all_posts)
             return

        # Filtrar por nuestra campaña
        my_posts = [p for p in all_posts if p.get('campaign_id') == campaign_id]
        
        if not my_posts:
            print("❌ No se encontraron posts para la campaña.")
            return

        post = my_posts[0]
        print("\n" + "="*50)
        print(f"📢 TÍTULO: {post.get('title')}")
        print("-" * 50)
        print(f"📝 CONTENIDO:\n{post.get('content_text')}")
        print("-" * 50)
        
        # Validación básica de reglas
        content = (post.get('content_text') or '').lower()
        limits = (target_identity.get('content_limits') or '').lower()
        
        print("\n🔍 ANÁLISIS AUTOMÁTICO:")
        if "emoji" in limits and any(char in content for char in "😀😃😄😁😆😅🤣😂🙂🙃😉😊😇🥰😍🤩😘😗☺😚😙😋😛😜🤪😛😜🤪😝🤑🤗🤭🤫🤔🤐🤨😐😑😶😏😒🙄😬🤥😌😔😪🤤😴😷🤒🤕🤢🤮🤧🥵🥶🥴😵🤯🤠🥳😎🤓🧐😕😟🙁☹😮😯😲😳🥺😦😧😨😰😥😢😭😱😖😣😞😓😩😫🥱😤😡😠🤬😈"):
             print("⚠️ ALERTA: Se detectaron emojis aunque los límites dicen 'no usar emojis'.")
        else:
             print("✅ Verificación de emojis: OK (respetados o no aplicables).")
             
        print("✅ Flujo completado exitosamente.")

    except Exception as e:
        print(f"❌ Error leyendo posts: {e}")

if __name__ == "__main__":
    run_mvp_flow()
