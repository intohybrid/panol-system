# ADR-013 — SSO federado como roadmap, JWT local en MVP

- **Estado**: Aceptada para MVP
- **Fecha**: 2026-04-25
- **Decisores**: Equipo Magíster

## Contexto

Toda escuela de una universidad ya tiene una infraestructura de identidad: un directorio (Active Directory / Entra ID / Google Workspace) donde los alumnos y docentes se autentican para correo, LMS y wifi. Lo natural en producción es que el Sistema de Pañol se integre a esa infraestructura vía OIDC / SAML, de modo que:

- El alumno use su cuenta institucional sin crear clave adicional.
- El alta/baja de usuarios se sincronice automáticamente con el sistema académico (SIS).
- La política de contraseñas, MFA, rotación y bloqueo se hereden del IdP central.

El Caso 11 no exige SSO; habla de "perfil con clave". La integración real, sin embargo, requiere coordinación organizacional con la Dirección de Tecnologías de la UNAB, credenciales de confianza con el IdP, y eventualmente certificación del sistema como relying party. Nada de eso cabe en la ventana del trabajo final.

## Decisión

El MVP usa **autenticación local con JWT**:

- Usuarios persisten en `auth-svc` con documento, clave hasheada (bcrypt ≥ 12), rol, carrera.
- Login devuelve JWT firmado con clave rotable (HS256 en MVP, RS256 cuando haya secrets manager).
- El JWT viaja como `Authorization: Bearer` y se valida en el API Gateway.
- Primer login fuerza cambio de clave (`RC.13`, `RF-C.10`).
- Clave inicial determinística: `{documento_valor}{sufijo_escuela}` (`SP.11 / CN.07`).

El SSO queda en roadmap como evolución natural con dos rutas posibles:

1. **Keycloak self-hosted** como IdP puente. Permite probar federación sin depender todavía del IdP institucional.
2. **Entra ID / Google Workspace directo**, cuando se cuente con credenciales y acuerdo de integración.

En ambos casos, la arquitectura no cambia: el API Gateway valida un JWT emitido por otro emisor, y `auth-svc` pasa a cumplir solo el rol de "perfiles y permisos" (no emite tokens).

## Alternativas consideradas

### Integración directa con SSO institucional en MVP

- **Pros**: producto final más cercano a producción real.
- **Contras**: bloquea el proyecto en dependencias externas (trámite de credenciales IdP, acuerdos con Dirección TI, test de federación). Imposible cumplir ventana académica. Vulnera `SP.09` (no hay integración con sistemas de la UNAB en MVP).

### Keycloak desde el MVP

- **Pros**: expone al equipo a OIDC realista sin depender del IdP institucional.
- **Contras**: agrega un contenedor más al compose, una base de datos más, configuración de realms y clients, y una curva de aprendizaje. El valor técnico que aporta (mostrar OIDC funcional) se obtiene con un trade-off alto para un equipo que además debe construir 9 microservicios.

### Solo sesiones stateful con cookie

- **Pros**: simpler en código.
- **Contras**: no escala entre microservicios sin compartir store de sesión. JWT es el estándar en arquitecturas distribuidas.

## Decisión justificada

JWT local es suficiente para demostrar RBAC, proteger endpoints y mostrar un flujo de seguridad coherente. Separar la responsabilidad en `auth-svc` como microservicio aislado mantiene el camino a SSO abierto: el día que se active SSO, la única pieza que cambia es quién emite el token. Todos los demás servicios siguen confiando en el JWT del header sin tocar código.

## Consecuencias

- `auth-svc` implementa: registro (por importación Excel / individual), login, cambio de clave, reset de clave, bloqueo/desbloqueo manual y automático.
- JWT con payload mínimo: `{sub, role, carreraId, iat, exp}`. Sin datos personales sensibles.
- Rotación de clave del JWT: variable `JWT_SECRET` por ambiente; en producción se rota desde secrets manager (no en MVP).
- Rate-limit de login (`RNF-SEC.3`): 5/min/IP, 10/h/usuario, bloqueo temporal de 15 min tras exceso.
- Roadmap técnico: `auth-svc` ya aisla la emisión de token en un `TokenIssuer` que puede reemplazarse por un validador de tokens externos.
- Defensa en mesa redonda: "separación de concerns anticipada. SSO es un cambio de adaptador, no un rediseño. El diseño ya está preparado".
