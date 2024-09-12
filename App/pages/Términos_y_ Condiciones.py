import streamlit as st

def main():



    st.set_page_config(
    st.title("📜 Términos de Servicio de Pasto Verde"),
    page_icon="🌿",
    layout="wide"
)

    st.write("""
    ¡Bienvenido a los términos de servicio de Pasto Verde! Al utilizar nuestros servicios, usted acepta los siguientes términos y condiciones:

    Dirección de Entrega
    El cliente es responsable de proporcionar una dirección de entrega correcta y accesible para recibir las alfombras de césped natural. Pasto Verde no se hace responsable por cualquier daño o deterioro ocurrido a la alfombra de césped después de la entrega exitosa en la dirección proporcionada.

    Responsabilidad Post-Entrega
    Pasto Verde no se responsabiliza por el estado del césped natural una vez que ha sido entregado en la dirección indicada por el cliente. Esto incluye daños causados por factores ambientales, mascotas u otros elementos fuera de nuestro control.

    Costos de Envío
    El costo de envío varía según el plan de suscripción o compra única seleccionada. Los cargos aplicables se detallarán al finalizar la compra y pueden estar sujetos a cambios según la ubicación y la modalidad de entrega seleccionada.

    Bases de Alfombras
    Las bases de las alfombras (de cartón, de madera normal o con drenaje) se venden por separado y pueden tener costos adicionales dependiendo de las opciones de personalización elegidas por el cliente.

    Cancelación de Suscripción
    El cliente puede cancelar su suscripción en cualquier momento. Sin embargo, no se realizarán reembolsos por el período pagado ya transcurrido. Se recomienda a los clientes gestionar la cancelación con antelación para evitar cargos no deseados.

    Modificaciones de Precios y Condiciones
    Pasto Verde se reserva el derecho de modificar los precios y las condiciones del servicio en cualquier momento. Se notificará al cliente de cualquier cambio con antelación adecuada para que pueda tomar decisiones informadas sobre la continuidad de su suscripción o compra.

    Reemplazo de Césped Natural
    Para garantizar la salud y bienestar de la mascota, se recomienda reemplazar el césped natural según el plan de suscripción elegido. El cliente es responsable de mantener el césped en condiciones adecuadas hasta su reemplazo.

    Propiedad Intelectual
    Todo el contenido, incluidas las imágenes generadas por inteligencia artificial, los gráficos, el diseño y la disposición de este sitio web, son propiedad exclusiva de Pasto Verde HN. Cualquier uso no autorizado de estos materiales está estrictamente prohibido.

    Cumplimiento Legal
    Pasto Verde se adhiere a todas las leyes y regulaciones aplicables en Honduras, incluyendo aquellas relacionadas con la protección del consumidor, privacidad y publicidad.

    Al utilizar nuestros servicios, usted acepta estos términos y condiciones. Si tiene alguna pregunta o inquietud, no dude en ponerse en contacto con nosotros.

    🔒 Política de Privacidad de Pasto Verde
    En Pasto Verde, nos comprometemos a proteger la privacidad y seguridad de nuestros clientes y visitantes. A continuación, describimos cómo manejamos la información personal y los datos que recopilamos.

    Recopilación de Información
    Cuando realizas una compra o suscripción en nuestro sitio, recopilamos información personal, como nombre, dirección y detalles de pago. Utilizamos esta información solo para procesar tu pedido y mejorar nuestros servicios.

    Uso de la Información
    Usamos la información recopilada para completar transacciones, enviar notificaciones de pedidos y mantener una comunicación constante sobre nuestras ofertas y actualizaciones. No compartimos tu información personal con terceros sin tu consentimiento explícito.

    Seguridad de los Datos
    Implementamos medidas de seguridad adecuadas para proteger tu información personal. Esto incluye el uso de cifrado y otros protocolos de seguridad. Aunque nos esforzamos por proteger tus datos, es importante tener en cuenta que ningún método de transmisión por Internet es 100% seguro.

    Cookies y Tecnologías Similares
    Utilizamos cookies para mejorar la experiencia del usuario en nuestra web. Estas cookies nos ayudan a entender cómo los visitantes usan nuestro sitio, lo que nos permite mejorar nuestras ofertas y servicios. Puedes desactivar las cookies en la configuración de tu navegador si prefieres no compartir esta información.

    Acceso y Corrección
    Tienes derecho a acceder a la información personal que hemos recopilado sobre ti y a corregir cualquier inexactitud. Si deseas revisar o actualizar tu información, puedes contactarnos en cualquier momento.

    Retención de Datos
    Conservamos tu información personal durante el tiempo que sea necesario para cumplir con los objetivos establecidos en esta política, a menos que la ley requiera o permita un período de retención más prolongado.

    Condiciones Especiales para Suscriptores
    Para nuestros clientes de suscripción, mantenemos información adicional sobre sus preferencias y envíos programados. Esto nos permite asegurar que recibas el mejor servicio posible y personalizar las entregas según tus necesidades.

    Cambios en la Política de Privacidad
    Podremos actualizar esta política ocasionalmente para reflejar cambios en nuestras prácticas o por razones legales o reglamentarias. Te animamos a revisar esta política regularmente para estar al tanto de cualquier modificación.

    En Pasto Verde, valoramos tu confianza en nosotros. Si tienes alguna pregunta o inquietud sobre nuestra política de privacidad, no dudes en contactarnos. Estamos aquí para ayudarte y asegurarnos de que tu experiencia con nosotros sea de la más alta calidad.
    """)

    st.write("Last updated: September 04, 2024")

    if st.button("Return to Home"):
        st.switch_page("App.py")

if __name__ == "__main__":
    main()
