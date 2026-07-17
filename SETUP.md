# Configuración del proyecto

Los siguientes archivos no se incluyen en el repositorio porque contienen configuración local o información sensible.

## 1. Backend

Crear el archivo:

```text
backend/.env
```

Con el siguiente contenido:

```env
OPENAI_API_KEY=your-api-key

OPENLIBRARY_USER_AGENT=Portafolio-BookSearch/1.0

# Providers
INTENT_PROVIDER=openai
GENERATION_PROVIDER=openai
EMBEDDING_PROVIDER=sentence-transformers

# Models
INTENT_MODEL=gpt-4.1-mini
GENERATION_MODEL=gpt-4.1-mini
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Retrieval
MAX_SEARCH_QUERIES=5
LIMIT_PER_QUERY=8
MAX_CANDIDATES_TO_ENRICH=15

# Generation
MAX_RESULTS_TO_GENERATE=5
MAX_RESULTS_TO_RETURN=15

# Networking
REQUEST_TIMEOUT=10
```

---

## 2. Frontend

Crear el archivo:

```text
frontend/.env.local
```

Con el siguiente contenido:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

---

## 3. Next.js

Verificar que exista el archivo:

```text
frontend/next-env.d.ts
```

Con el siguiente contenido:

```ts
/// <reference types="next" />
/// <reference types="next/image-types/global" />
import "./.next/dev/types/routes.d.ts";

// NOTE: This file should not be edited
// see https://nextjs.org/docs/app/api-reference/config/typescript for more information.
```