# RabbitMQ 3.12 + plugin de delayed messages para soportar Message Expiration
# (EIP-03) usando un exchange x-delayed-message.
#
# El plugin oficial NO viene incluido en la imagen base, así que lo bajamos
# desde el release oficial de rabbitmq/rabbitmq-delayed-message-exchange.
# Ver: https://github.com/rabbitmq/rabbitmq-delayed-message-exchange

FROM rabbitmq:3.12-management

ARG DELAYED_PLUGIN_VERSION=3.12.0

# Descargar el plugin .ez al directorio de plugins de RabbitMQ
ADD --chown=rabbitmq:rabbitmq \
    https://github.com/rabbitmq/rabbitmq-delayed-message-exchange/releases/download/v${DELAYED_PLUGIN_VERSION}/rabbitmq_delayed_message_exchange-${DELAYED_PLUGIN_VERSION}.ez \
    /opt/rabbitmq/plugins/rabbitmq_delayed_message_exchange-${DELAYED_PLUGIN_VERSION}.ez

# Lista de plugins habilitados (sobreescribe el default)
COPY enabled_plugins /etc/rabbitmq/enabled_plugins

# Cargar definiciones (exchanges, colas, bindings) al iniciar
RUN echo "management.load_definitions = /etc/rabbitmq/definitions.json" \
    >> /etc/rabbitmq/conf.d/10-defaults.conf
