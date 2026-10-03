import smtplib, time, random, sys, datetime, os
from email.mime.text import MIMEText
from email.utils import formataddr

def load_env(env_path):
    config = {}
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.split('=', 1)
                config[k.strip()] = v.strip().strip('"').strip("'")
    return config

env = load_env('/Users/ejimenezsys/Desktop/sitiosweb/agencia/.env')
u = env.get('SMTP_USER')
p = env.get('SMTP_PASSWORD')
h = env.get('SMTP_HOST')
port = int(env.get('SMTP_PORT', 465))
notification_target = "edward@exmaglobal.com"

signature = """Edward Jiménez
Partner Relationship Manager · EXMA Global
edward@exmaglobal.com
exmaglobal.com/miami"""

# 29 Prospectos Auditados para Martes: 19 VALID (Cero rebote) + 10 CATCH-ALL (Incierto sin rebote)
prospects = [
    # --- 19 VERIFICADOS VALID (Buzón real confirmado en servidor) ---
    {
        "empresa": "Banesco USA",
        "destinatario": "Carlos Lamourtte",
        "email": "clamourtte@banescousa.com",
        "tipo": "VALID",
        "asunto": "Banesco nació para nuestra comunidad. Queremos que esté en su escenario.",
        "cuerpo": f"""Hola Carlos:

Seguí de cerca el trimestre que reportaron en Banesco USA: 38% de crecimiento en utilidad y más de mil millones en depósitos en Puerto Rico. Es de las pocas historias de banca hispana en Estados Unidos que crece a ese ritmo y sigue siendo de los suyos.

Banesco es de esas marcas que están aquí para servir a nuestra gente. Por eso le escribo.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, emprendedores y profesionales hispanos. Es el primer gran evento de una plataforma que celebra a hispanos ordinarios haciendo cosas extraordinarias.

Estamos invitando a una sola marca por categoría. Nos encantaría que en banca fuera Banesco: el banco que acompañó a esta comunidad desde el principio, ahora en su escenario.

¿Tiene 15 minutos esta semana o la próxima para contarle cómo funcionaría?

Un abrazo,

{signature}"""
    },
    {
        "empresa": "Cacique Foods",
        "destinatario": "Pedro Silveira",
        "email": "psilveira@caciqueinc.com",
        "tipo": "VALID",
        "asunto": "Cacique nació para nuestra comunidad. Queremos que esté en su escenario.",
        "cuerpo": f"""Hola Pedro:

Vi su llegada a Cacique el año pasado después de Mondelēz. Tomar una marca familiar hispana y llevarla a otra escala es un tipo de reto distinto al de una multinacional, y es justo la conversación que vamos a tener en diciembre.

Cacique es de esas marcas que nacieron aquí para servir a nuestra gente. Por eso le escribo.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, emprendedores y profesionales hispanos.

Estamos invitando a una sola marca por categoría. Nos encantaría que en su categoría fuera Cacique.

¿Tiene 15 minutos esta semana o la próxima?

Un abrazo,

{signature}"""
    },
    {
        "empresa": "F. Gaviña & Sons (Café La Llave)",
        "destinatario": "Leonor Gaviña-Valls",
        "email": "leonor.gavina@gavina.com",
        "tipo": "VALID",
        "asunto": "Gaviña nació para nuestra comunidad. Queremos que esté en su escenario.",
        "cuerpo": f"""Hola Leonor:

Vi el lanzamiento de las cápsulas reciclables de Café La Llave. Que una marca que empezó con una familia cubana llegando a Los Ángeles esté hoy marcando la pauta en su categoría es exactamente la historia que nos interesa contar.

Gaviña es de esas marcas que nacieron aquí para servir a nuestra gente. Por eso le escribo.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, emprendedores y profesionales hispanos. Es el primer gran evento de una plataforma que celebra a hispanos ordinarios haciendo cosas extraordinarias.

Estamos invitando a una sola marca por categoría. Nos encantaría que en café fuera Gaviña.

¿Tiene 15 minutos esta semana o la próxima?

Un abrazo,

{signature}"""
    },
    {
        "empresa": "Bacardi USA",
        "destinatario": "Ned Duggan",
        "email": "nduggan@bacardi.com",
        "tipo": "VALID",
        "asunto": "Bacardi nació para nuestra comunidad. Queremos que esté en su escenario.",
        "cuerpo": f"""Hola Ned:

Bacardi lleva más de un siglo siendo la historia de una familia que empezó de nuevo y construyó algo global desde el Caribe. Esa es literalmente la historia que vamos a poner en un escenario en diciembre.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, emprendedores y profesionales hispanos.

Sé que su rol es global y que esto es una activación regional en el sur de Florida. ¿Me podría indicar con quién hablar del equipo de Bacardi en Coral Gables? Con mucho gusto le escribo directamente.

Un abrazo,

{signature}"""
    },
    {
        "empresa": "Pollo Tropical",
        "destinatario": "Enrique Perez-Pantera",
        "email": "eperez@pollotropical.com",
        "tipo": "VALID",
        "asunto": "Pollo Tropical nació para nuestra comunidad. Queremos que esté en su escenario.",
        "cuerpo": f"""Hola Enrique:

Pollo Tropical es una institución del sabor latino en el sur de la Florida. Desde hace décadas, su menú y su presencia representan el día a día de millones de familias y profesionales hispanos en este estado.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, emprendedores y profesionales hispanos.

Estamos invitando a una sola marca por categoría. Nos encantaría que en restaurantes fuera Pollo Tropical.

¿Tiene 15 minutos esta semana o la próxima para contarle cómo funcionaría?

Un abrazo,

{signature}"""
    },
    {
        "empresa": "Deloitte US",
        "destinatario": "Scott Mager",
        "email": "smager@deloitte.com",
        "tipo": "VALID",
        "asunto": "La comunidad de doers hispanos más grande de Estados Unidos",
        "cuerpo": f"""Hola Scott:

Deloitte publica año tras año sobre el poder de compra hispano en Estados Unidos. En diciembre esa audiencia no va a estar en un informe: va a estar en una sala.

Deloitte apoya a quienes emprenden, innovan y crecen. Nosotros reunimos exactamente a esas personas, en español y con alma latina.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos: emprendedores, profesionales y dueños de negocio. Dos días de marketing, innovación, estrategia, inversiones y finanzas para una comunidad que no deja de crecer.

Buscamos una sola marca por categoría que se convierta en la que impulsa ese crecimiento: en el escenario, en el contenido y en la comunidad que sigue viva después del evento.

¿Tiene 15 minutos esta semana o la próxima para contarle cómo lo imaginamos para Deloitte?

Saludos,

{signature}"""
    },
    {
        "empresa": "Intuit",
        "destinatario": "Thomas Ranese",
        "email": "thomas_ranese@intuit.com",
        "tipo": "VALID",
        "asunto": "La comunidad de doers hispanos más grande de Estados Unidos",
        "cuerpo": f"""Hola Thomas:

QuickBooks vive de los dueños de negocio pequeños, y el segmento que más rápido crece en ese universo es el hispano. En diciembre hay 2.500 de ellos en una sala.

Intuit apoya a quienes emprenden, innovan y crecen. Nosotros reunimos exactamente a esas personas, en español y con alma latina.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos: emprendedores, profesionales y dueños de negocio. Dos días de marketing, innovación, estrategia, inversiones y finanzas para una comunidad que no deja de crecer.

Buscamos una sola marca por categoría que se convierta en la que impulsa ese crecimiento: en el escenario, en el contenido y en la comunidad que sigue viva después del evento.

¿Tiene 15 minutos esta semana o la próxima para contarle cómo lo imaginamos para Intuit?

Saludos,

{signature}"""
    },
    {
        "empresa": "Diageo North America",
        "destinatario": "Cristina Diezhandino",
        "email": "cristina.diezhandino@diageo.com",
        "tipo": "VALID",
        "asunto": "2.500 líderes hispanos en Miami. Una sola marca de licores.",
        "cuerpo": f"""Hola Cristina:

El consumidor hispano es de los que más crece en su categoría en Estados Unidos, tanto en marcas icónicas como Don Julio y Casamigos como en el portafolio global de Diageo.

Sé que su equipo invierte en llegarle al consumidor hispano. Le propongo algo que un anuncio no puede dar: estar en la sala.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, emprendedores y profesionales hispanos.

Trabajamos con exclusividad por categoría. En licores, solo habrá una marca en el escenario, en la experiencia y en el contenido del evento.

Si aún tiene presupuesto de cierre de año para comunidad o experiencias, es un buen momento para conversar. ¿Tiene 15 minutos esta semana o la próxima?

Saludos,

{signature}"""
    },
    {
        "empresa": "The J.M. Smucker Co. (Café Bustelo)",
        "destinatario": "Katie Williams",
        "email": "katie.williams@jmsmucker.com",
        "tipo": "VALID",
        "asunto": "2.500 líderes hispanos en Miami. Una sola marca de café.",
        "cuerpo": f"""Hola Katie:

Café Bustelo es de las pocas marcas grandes que esta comunidad siente como propia en cada hogar latino de Florida y de todo Estados Unidos.

Sé que su equipo invierte en llegarle al consumidor hispano. Le propongo algo que un anuncio no puede dar: estar en la sala.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos y dueños de negocio.

Trabajamos con exclusividad por categoría. En café, solo habrá una marca en el escenario y en la experiencia del evento.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

{signature}"""
    },
    {
        "empresa": "Lowe's Companies",
        "destinatario": "Marvin Ellison",
        "email": "marvin.ellison@lowes.com",
        "tipo": "VALID",
        "asunto": "2.500 líderes hispanos en Miami. Una sola marca de mejoras para el hogar.",
        "cuerpo": f"""Hola Marvin:

Buena parte del contratista y profesional que compra en Lowe's en Florida y Texas es hispano y dueño de su propio negocio. Esa es exactamente la mitad de esta sala.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, emprendedores y profesionales hispanos.

Trabajamos con exclusividad por categoría. En mejoras para el hogar y retail especializado, solo habrá una marca en el escenario.

¿Tiene su equipo 15 minutos esta semana o la próxima para conversar?

Saludos,

{signature}"""
    },
    {
        "empresa": "Best Buy Co",
        "destinatario": "Jennie Weber",
        "email": "jennie.weber@bestbuy.com",
        "tipo": "VALID",
        "asunto": "2.500 líderes hispanos en Miami. Una sola marca de electrónica.",
        "cuerpo": f"""Hola Jennie:

El comprador hispano está sobreindexado en adopción de tecnología en Estados Unidos. En diciembre hay 2.500 de ellos, y son quienes deciden las compras tecnológicas en sus empresas y hogares.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.

Trabajamos con exclusividad por categoría. En electrónica y retail tecnológico, solo habrá una marca en el escenario.

¿Tiene 15 minutos esta semana o la próxima?

Saludos,

{signature}"""
    },
    {
        "empresa": "Burger King (Restaurant Brands International)",
        "destinatario": "Tom Curtis",
        "email": "tcurtis@rbi.com",
        "tipo": "VALID",
        "asunto": "2.500 líderes hispanos en Miami. Una sola marca de restaurantes.",
        "cuerpo": f"""Hola Tom:

Burger King tiene su casa en Miami y su consumidor hispano es central para el negocio. Los dos coinciden el 4 y 5 de diciembre a minutos de su sede central.

EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes y profesionales hispanos.

Trabajamos con exclusividad por categoría. En restaurantes de servicio rápido, solo habrá una marca en el escenario y en el contenido.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

{signature}"""
    },
    {
        "empresa": "Carnival Cruise Line",
        "destinatario": "Christine Duffy",
        "email": "cduffy@carnival.com",
        "tipo": "VALID",
        "asunto": "2.500 líderes hispanos en Miami. Una sola naviera en el escenario.",
        "cuerpo": f"""Hola Christine:

Carnival es de Miami como pocas marcas. En diciembre la ciudad reúne a 2.500 líderes hispanos, y el viajero hispano es de los segmentos familiares que más rápido crece para la industria de cruceros.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a esta comunidad.

Trabajamos con exclusividad por categoría. En cruceros, solo habrá una marca en el escenario y en la experiencia.

¿Tiene 15 minutos esta semana o la próxima?

Saludos,

{signature}"""
    },
    {
        "empresa": "Coca-Cola Beverages Florida",
        "destinatario": "Troy Taylor",
        "email": "ttaylor@cocacolaflorida.com",
        "tipo": "VALID",
        "asunto": "2.500 líderes hispanos en Miami. Una sola marca de bebidas.",
        "cuerpo": f"""Hola Troy:

Coke Florida embotella justo en el estado donde la población hispana crece más rápido y con mayor poder de compra. Ese consumidor y sus empleadores van a estar reunidos en una sala en diciembre.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.

Trabajamos con exclusividad por categoría. En bebidas, solo habrá una marca en el escenario y en la hidratación oficial del evento.

¿Tiene 15 minutos esta semana o la próxima?

Saludos,

{signature}"""
    },
    {
        "empresa": "Colgate-Palmolive",
        "destinatario": "Carolina Incognito",
        "email": "carolina_incognito@colpal.com",
        "tipo": "VALID",
        "asunto": "2.500 líderes hispanos en Miami. Una sola marca de cuidado personal.",
        "cuerpo": f"""Hola Carolina:

Su liderazgo en marketing multicultural refleja exactamente lo que es esta sala: Latinoamérica y Estados Unidos reunidos en un mismo lugar de alto impacto.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.

Trabajamos con exclusividad por categoría. En cuidado personal y salud oral, solo habrá una marca en el escenario.

¿Tiene 15 minutos esta semana o la próxima?

Saludos,

{signature}"""
    },
    {
        "empresa": "Constellation Brands",
        "destinatario": "Jim Sabia",
        "email": "jim.sabia@cbrands.com",
        "tipo": "VALID",
        "asunto": "2.500 líderes hispanos en Miami. Una sola marca de cerveza.",
        "cuerpo": f"""Hola Jim:

Modelo Especial y Corona son, en la práctica, la cerveza de referencia de esta comunidad en Estados Unidos.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, emprendedores y profesionales hispanos.

Trabajamos con exclusividad por categoría. En cerveza, habrá una sola marca en el escenario y en las experiencias VIP del evento.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

{signature}"""
    },
    {
        "empresa": "The Wendy's Company",
        "destinatario": "Lindsay Radkoski",
        "email": "lindsay.radkoski@wendys.com",
        "tipo": "VALID",
        "asunto": "2.500 líderes hispanos en Miami. Una sola marca de restaurantes.",
        "cuerpo": f"""Hola Lindsay:

El crecimiento de su categoría en el sur de Estados Unidos pasa por el consumidor hispano y la lealtad de marca familiar. En diciembre esa audiencia está en una sola sala.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.

Trabajamos con exclusividad por categoría. En restaurantes de servicio rápido, solo habrá una marca en el escenario.

¿Tiene 15 minutos esta semana o la próxima?

Saludos,

{signature}"""
    },
    {
        "empresa": "The Hershey Company",
        "destinatario": "David Wrubleski",
        "email": "dwrubleski@hersheys.com",
        "tipo": "VALID",
        "asunto": "2.500 líderes hispanos en Miami. Una sola marca de confitería y snacks.",
        "cuerpo": f"""Hola David:

El consumidor hispano es uno de los mayores motores de compra en confitería y snacks en Estados Unidos, con una lealtad de marca altísima.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes y familias empresarias hispanas.

Trabajamos con exclusividad por categoría. En confitería y snacks, solo habrá una marca en el escenario.

¿Tiene 15 minutos esta semana o la próxima?

Saludos,

{signature}"""
    },
    {
        "empresa": "Walmart Inc.",
        "destinatario": "William White",
        "email": "william.white@walmart.com",
        "tipo": "VALID",
        "asunto": "2.500 líderes hispanos en Miami. Una sola marca de retail.",
        "cuerpo": f"""Hola William:

Walmart lleva años construyendo una relación sólida y auténtica con el comprador hispano. Le propongo el lugar donde ese comprador no solo compra, sino que se reúne a hacer negocios y liderar.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes y emprendedores hispanos.

Trabajamos con exclusividad por categoría. En retail, solo habrá una marca en el escenario.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

{signature}"""
    },

    # --- 10 AUDITADOS CATCH-ALL (Inciertos: no rebotan, pero entrega humana no garantizada) ---
    {
        "empresa": "PwC US",
        "destinatario": "Antonia Wade",
        "email": "antonia.wade@pwc.com",
        "tipo": "CATCH_ALL",
        "asunto": "La comunidad de doers hispanos más grande de Estados Unidos",
        "cuerpo": f"""Hola Antonia:

Escribo en español a propósito: es el idioma de los 2.500 líderes de negocio que se reúnen en Miami en diciembre, y de un mercado que su firma ya analiza de cerca.

PwC apoya a quienes emprenden, innovan y crecen. Nosotros reunimos exactamente a esas personas, en español y con alma latina.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.

Buscamos una sola marca por categoría que impulse ese crecimiento en el escenario y en la comunidad.

¿Tiene 15 minutos esta semana o la próxima para contarle cómo lo imaginamos para PwC?

Saludos,

{signature}"""
    },
    {
        "empresa": "Workday",
        "destinatario": "Emma Chalwin",
        "email": "emma.chalwin@workday.com",
        "tipo": "CATCH_ALL",
        "asunto": "La comunidad de doers hispanos más grande de Estados Unidos",
        "cuerpo": f"""Hola Emma:

El 54% de los asistentes a EXMA Miami son corporativos y el resto emprendedores. Es, literalmente, la sala de sus dos compradores a la vez.

Workday apoya a quienes emprenden, innovan y crecen. Nosotros reunimos exactamente a esas personas, en español y con alma latina.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.

¿Tiene 15 minutos esta semana o la próxima para contarle cómo lo imaginamos para Workday?

Saludos,

{signature}"""
    },
    {
        "empresa": "Charles Schwab",
        "destinatario": "Lisa Ross",
        "email": "lisa.ross@schwab.com",
        "tipo": "CATCH_ALL",
        "asunto": "2.500 líderes hispanos en Miami. Una sola institución de inversiones.",
        "cuerpo": f"""Hola Lisa:

La comunidad de inversionistas y emprendedores hispanos en Estados Unidos crece a un ritmo superior a la media nacional en apertura de cuentas patrimoniales.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.

Trabajamos con exclusividad por categoría. En servicios de inversión y gestión patrimonial, solo habrá una marca en el escenario.

¿Tiene 15 minutos esta semana o la próxima?

Saludos,

{signature}"""
    },
    {
        "empresa": "Florida Power & Light (FPL / NextEra Energy)",
        "destinatario": "Kimberly Blair",
        "email": "kimberly.blair@fpl.com",
        "tipo": "CATCH_ALL",
        "asunto": "2.500 líderes hispanos en Miami. Una sola marca de energía.",
        "cuerpo": f"""Hola Kimberly:

Su equipo de relaciones con la comunidad trabaja el sur de Florida todos los días. Esto es esa comunidad empresarial y profesional, concentrada en dos días.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.

Trabajamos con exclusividad por categoría. En energía y sostenibilidad, solo habrá una marca en el escenario.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

{signature}"""
    },
    {
        "empresa": "Mondelēz International",
        "destinatario": "Mie-Leng Wong",
        "email": "mie-leng.wong@mdlz.com",
        "tipo": "CATCH_ALL",
        "asunto": "2.500 líderes hispanos en Miami. Una sola marca de snacks.",
        "cuerpo": f"""Hola Mie-Leng:

Mondelēz creció en este mercado a punta de entender y acompañar al consumidor hispano en cada momento de consumo.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos. Esta es la sala donde ese consumidor decide y lidera.

Trabajamos con exclusividad por categoría. En snacks y galletas, solo habrá una marca en el escenario.

¿Tiene 15 minutos esta semana o la próxima?

Saludos,

{signature}"""
    },
    {
        "empresa": "New York Life Insurance Company",
        "destinatario": "Amy Hu",
        "email": "amy_hu@newyorklife.com",
        "tipo": "CATCH_ALL",
        "asunto": "2.500 líderes hispanos en Miami. Una sola aseguradora de vida y patrimonio.",
        "cuerpo": f"""Hola Amy:

New York Life tiene una de las trayectorias más profundas sirviendo a familias empresarias y profesionales hispanos en protección financiera.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 tomadores de decisión hispanos.

Trabajamos con exclusividad por categoría. En seguros de vida y patrimonio, solo habrá una marca en el escenario.

¿Tiene 15 minutos esta semana o la próxima?

Saludos,

{signature}"""
    },
    {
        "empresa": "Nissan North America",
        "destinatario": "Marisstella Marinkovic",
        "email": "marisstella.marinkovic@nissan-usa.com",
        "tipo": "CATCH_ALL",
        "asunto": "2.500 líderes hispanos en Miami. Una sola marca automotriz.",
        "cuerpo": f"""Hola Marisstella:

El comprador hispano es de los segmentos más leales y de mayor crecimiento en el sector automotriz en Estados Unidos.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos.

Trabajamos con exclusividad por categoría. En automotriz, habrá una sola marca oficial en el escenario y en la exhibición exterior del evento.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

{signature}"""
    },
    {
        "empresa": "Procter & Gamble (P&G)",
        "destinatario": "Marc Pritchard",
        "email": "pritchard.m@pg.com",
        "tipo": "CATCH_ALL",
        "asunto": "2.500 líderes hispanos en Miami. Una sola marca de consumo masivo.",
        "cuerpo": f"""Hola Marc:

P&G ha sido de las compañías más explícitas y consistentes del país sobre representación cultural y apoyo a la comunidad hispana.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes hispanos. Hay un escenario donde esa conversación ocurre en español y con acción real.

Trabajamos con exclusividad por categoría. Nos encantaría explorar si P&G tiene espacio para estar presente.

¿Tiene su equipo 15 minutos esta semana o la próxima?

Saludos,

{signature}"""
    },
    {
        "empresa": "The Kraft Heinz Company",
        "destinatario": "Diana Frost",
        "email": "diana.frost@kraftheinz.com",
        "tipo": "CATCH_ALL",
        "asunto": "2.500 líderes hispanos en Miami. Una sola marca de alimentos.",
        "cuerpo": f"""Hola Diana:

El consumidor hispano es uno de los mayores motores de volumen y crecimiento en alimentos y condimentos en Estados Unidos.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes y familias hispanas.

Trabajamos con exclusividad por categoría. En alimentos empacados, solo habrá una marca en el escenario.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

{signature}"""
    },
    {
        "empresa": "Western Union",
        "destinatario": "Devin McGranahan",
        "email": "devin.mcgranahan@westernunion.com",
        "tipo": "CATCH_ALL",
        "asunto": "2.500 líderes hispanos en Miami. Una sola marca de servicios financieros transfronterizos.",
        "cuerpo": f"""Hola Devin:

Western Union existe y ha crecido de la mano de esta comunidad. En diciembre está reunida en un solo lugar, a minutos de las principales rutas financieras de las Américas.

El 4 y 5 de diciembre, EXMA reúne en Downtown Event Center, Fort Lauderdale (área de Miami) a 2.500 líderes, empresarios y profesionales hispanos.

Trabajamos con exclusividad por categoría. En servicios transfronterizos y pagos, solo habrá una marca en el escenario.

¿Tiene 15 minutos esta semana o la próxima para conversar?

Saludos,

{signature}"""
    }
]

def send_alert(server, subject, body):
    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = formataddr(('EXMA Outreach System', u))
        msg['To'] = formataddr(('Edward Jimenez', notification_target))
        server.sendmail(u, [notification_target], msg.as_string())
        print(f"🔔 Alerta enviada a tu móvil ({notification_target}): {subject}")
    except Exception as e:
        print(f"No se pudo enviar alerta: {e}")

def run_campaign():
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    val_count = sum(1 for p in prospects if p['tipo'] == 'VALID')
    catch_count = sum(1 for p in prospects if p['tipo'] == 'CATCH_ALL')
    
    print(f"\n==================================================")
    print(f"🚀 INICIANDO DESPACHO PLAN EXTENDIDO ({len(prospects)} CORREOS)")
    print(f"Composición: {val_count} VALID (100% verificados) + {catch_count} CATCH-ALL (Inciertos sin rebote)")
    print(f"Hora de inicio: {now_str}")
    print(f"Servidor SMTP: {h}:{port}")
    print(f"==================================================\n")
    
    server = smtplib.SMTP_SSL(h, port, timeout=20)
    server.login(u, p)
    
    send_alert(
        server,
        f"🚀 [EXMA Outreach] Arrancó el despacho de los {len(prospects)} correos del Martes",
        f"Hola Edward,\n\nSe acaba de iniciar el despacho automático del Plan Extendido ({len(prospects)} correos):\n- {val_count} VALID (Cero rebote)\n- {catch_count} CATCH-ALL (Inciertos, sin rebote)\n\nSe aplican pausas humanas de 75 a 110 segundos entre cada uno. Te llegará el reporte final al terminar."
    )
    
    success_count = 0
    error_count = 0
    delivery_log = []
    
    for idx, p_info in enumerate(prospects, 1):
        empresa = p_info['empresa']
        nombre_dest = p_info['destinatario']
        to_email = p_info['email']
        tipo = p_info['tipo']
        asunto = p_info['asunto']
        cuerpo = p_info['cuerpo']
        
        msg = MIMEText(cuerpo, 'plain', 'utf-8')
        msg['Subject'] = asunto
        msg['From'] = formataddr(('Edward Jiménez · EXMA Global', u))
        msg['To'] = formataddr((nombre_dest, to_email))
        msg['Reply-To'] = 'edward@exmaglobal.com'
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        try:
            server.sendmail(u, [to_email], msg.as_string())
            print(f"[{idx}/{len(prospects)}] ✅ {timestamp} [{tipo}] ENVIADO: {nombre_dest} ({empresa}) <{to_email}>")
            success_count += 1
            delivery_log.append(f"✅ {timestamp} [{tipo}] {empresa}: {nombre_dest} <{to_email}>")
        except Exception as e:
            print(f"[{idx}/{len(prospects)}] ❌ {timestamp} [{tipo}] ERROR con {to_email}: {e}")
            error_count += 1
            delivery_log.append(f"❌ {timestamp} [{tipo}] {empresa}: {nombre_dest} (Error: {e})")
            
        if idx < len(prospects):
            sleep_time = random.randint(75, 110)
            print(f"   ⏳ Pausa humana anti-spam: esperando {sleep_time}s antes del siguiente...")
            time.sleep(sleep_time)
            
    finish_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    send_alert(
        server,
        f"🎉 [EXMA Outreach] Despacho completado ({success_count}/{len(prospects)} enviados)",
        f"Hola Edward,\n\nEl despacho del Plan Extendido de hoy martes ha finalizado exitosamente.\n\nResumen:\n- Total enviados: {success_count}\n- Errores de envío: {error_count}\nHora finalización: {finish_str}\n\nDetalle:\n" + "\n".join(delivery_log) + "\n\nCualquier respuesta de los C-Levels llegará directo a tu bandeja de edward@exmaglobal.com."
    )
    
    server.quit()
    print("\n🎉 ¡DESPACHO DEL BLOQUE COMPLETADO CON ÉXITO!")

def wait_until_target(target_hour=9, target_minute=0):
    now = datetime.datetime.now()
    if now.hour > target_hour or (now.hour == target_hour and now.minute >= target_minute):
        target = now.replace(day=now.day + 1, hour=target_hour, minute=target_minute, second=0, microsecond=0)
    else:
        target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        
    diff = (target - now).total_seconds()
    print(f"⏳ PROGRAMADOR ACTIVO: Esperando hasta las {target.strftime('%Y-%m-%d %H:%M:%S')} ({diff/3600:.2f} horas)...")
    
    while True:
        current = datetime.datetime.now()
        remaining = (target - current).total_seconds()
        if remaining <= 0:
            print("⏰ ¡HORA ALCANZADA! Iniciando campaña...")
            break
        sleep_dur = min(30, remaining)
        time.sleep(sleep_dur)
        
    run_campaign()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--schedule':
        wait_until_target(9, 0)
    else:
        run_campaign()
