# ADR-009 — Arquitectura cloud-agnóstica en lugar de comprometerse con AWS/Azure/GCP

- **Estado**: Aceptada
- **Fecha**: 2026-04-18
- **Decisores**: Equipo Magíster

## Contexto

El despliegue del sistema podría apoyarse fuertemente en servicios gestionados de un cloud específico: SQS/SNS o EventBridge en AWS, Service Bus en Azure, Pub/Sub en GCP, RDS en cualquiera, Lambda/Functions, Secrets Manager, etc. La rúbrica del Caso 11 valora la calidad arquitectónica genérica y no exige cloud específico. La universidad UNAB no tiene un proveedor cloud impuesto al equipo. El equipo es de Magíster sin experiencia profunda en ningún cloud.

## Decisión

Diseñar la arquitectura de modo **cloud-agnóstico**: usar abstracciones (broker, BD relacional, compute, object storage, secrets) que se mapean a cualquier proveedor o a infraestructura on-prem sin cambios estructurales. No usar servicios gestionados específicos de un cloud para piezas centrales.

## Alternativas consideradas

### Comprometerse con AWS

- **Pros**: Stack más conocido en el mercado chileno, mucha literatura.
- **Contras**: Vendor lock-in. La rúbrica no premia "AWS bien hecho" más que "diseño bien hecho". El equipo no tiene cuenta institucional con créditos garantizados.

### Comprometerse con Azure (vía Microsoft for Education)

- **Pros**: La universidad podría tener acuerdos con Microsoft.
- **Contras**: No verificado. Mismo riesgo de lock-in.

### Diseño cloud-agnóstico (la elegida)

- **Pros**:
  - Defendible en mesa redonda sin tener que justificar un cloud específico.
  - Portable a cualquier proveedor o a un servidor físico de la escuela.
  - Las abstracciones genéricas son las correctas conceptualmente: "broker", "BD", "compute" son los conceptos del libro de Hohpe y de los textos de arquitectura; los servicios gestionados son su instanciación, no la abstracción.
- **Contras**:
  - Operación manual en producción (instalar RabbitMQ, Postgres, gestionar despliegue) en lugar de "click & go".
  - Para producción real probablemente se elegiría un cloud y servicios gestionados; el diseño actual lo permite sin reescribir.

## Decisión justificada

El objetivo del MVP es demostrar arquitectura limpia y patrones explícitos, no operación productiva. Cloud-agnóstico es la forma más directa de mostrar el diseño en su capa correcta.

## Consecuencias

- Componentes empaquetados en Docker. `docker-compose.yml` levanta el sistema completo en local.
- En producción, despliegue como contenedores en cualquier orquestador (Kubernetes, ECS, AKS, GKE, Nomad, o un VPS con docker-compose).
- Configuración por variables de entorno validadas con Zod al boot.
- Object storage abstraído por una interfaz `StorageAdapter` (implementaciones: filesystem local, S3-compatible). Útil para PDFs de tickets si se externaliza el almacenamiento.
- Secrets gestionados por variables de entorno o por un adaptador (Vault, Secrets Manager, Key Vault) que se decide en deployment, no en código.
- La defensa: "el diseño no se ata; el costo de adoptar un cloud específico en el futuro es de configuración, no de arquitectura".

## Roadmap

Si el sistema entra en producción y la escuela elige un cloud:

- **AWS**: RDS Postgres, RabbitMQ on EC2 o Amazon MQ, ECS Fargate para los servicios, S3 para PDFs, Secrets Manager.
- **Azure**: Database for PostgreSQL, RabbitMQ on AKS o Service Bus (cambia la implementación EIP), Container Apps, Blob Storage, Key Vault.
- **GCP**: Cloud SQL, RabbitMQ on GKE, Cloud Run, Cloud Storage, Secret Manager.

Cada migración es trabajo de DevOps, no de arquitectura.
