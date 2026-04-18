
# Blogging API

REST API para gestión de blogs construida con FastAPI, SQLAlchemy y MySQL. Permite registrar usuarios, crear posts con categorías y tags, y publicarlos con autenticación JWT.

---

## Instalación y ejecución

```bash
# 0. CLonar el repo
git clone https://roadmap.sh/projects/blogging-platform-api

# 1. Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno (ver sección siguiente)

# 4. Correr migraciones
alembic upgrade head

# 5. Iniciar servidor
uvicorn app.main:app --reload
```

La API estará disponible en `http://localhost:8000`. Documentación interactiva en `http://localhost:8000/docs`.

---

## Variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
DATABASE_URL=mysql+pymysql://<user>:<password>@<host>:<port>/<database>
SECRET_KEY=<clave_secreta_aleatoria>
```

---

## Endpoints

### Auth

| Método | Ruta              | Descripción        | Auth |
| ------ | ----------------- | ------------------ | ---- |
| POST   | `/auth/register`  | Registrar usuario  | No   |
| POST   | `/auth/login`     | Login, retorna JWT | No   |

### Posts

| Método | Ruta                              | Descripción                               | Auth       |
| ------ | --------------------------------- | ----------------------------------------- | ---------- |
| POST   | `/posts/`                         | Crear post                                | Si         |
| GET    | `/posts/`                         | Listar posts paginados (`?page`, `?limit`)   | No         |
| GET    | `/posts/{post_id}`                | Obtener post por ID                       | No         |
| PUT    | `/posts/{post_id}`                | Actualizar post                           | Si (dueño) |
| DELETE | `/posts/{post_id}`                | Eliminar post                             | Si (dueño) |
| PATCH  | `/posts/{post_id}/publish`        | Publicar post                             | Si (dueño) |
| POST   | `/posts/{post_id}/tags/{tag_id}`  | Agregar tag a post                        | Si (dueño) |
| DELETE | `/posts/{post_id}/tags/{tag_id}`  | Quitar tag de post                        | Si (dueño) |

### Categories

| Método | Ruta                      | Descripción        | Auth |
| ------ | ------------------------- | ------------------ | ---- |
| POST   | `/categories/`            | Crear categoría    | Si   |
| GET    | `/categories/`            | Listar categorías  | No   |
| DELETE | `/categories/{category_id}` | Eliminar categoría | Si |

### Tags

| Método | Ruta           | Descripción  | Auth |
| ------ | -------------- | ------------ | ---- |
| POST   | `/tags/`       | Crear tag    | Si   |
| GET    | `/tags/`       | Listar tags  | No   |
| DELETE | `/tags/{tag_id}` | Eliminar tag | Si |

> Los endpoints con **Auth: Si** requieren el header `Authorization: Bearer <token>` obtenido en `/auth/login`.
