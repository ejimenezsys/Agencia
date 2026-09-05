# PROSPERIA Intelligence

## Decisión estratégica

El antiguo blog de noticias se convierte en el activo editorial canónico del ecosistema.
No persigue volumen de noticias: transforma señales tecnológicas en criterio y decisiones.

- **Objetivo:** construir autoridad transferible hacia conferencias, mentorías y consultoría.
- **Cuello de botella:** contenido genérico, sin trazabilidad y sin separación de autorías.
- **KPI principal:** conversaciones calificadas originadas en contenido.
- **KPI de autoridad:** menciones, invitaciones, enlaces y suscriptores ejecutivos.
- **KPI de distribución:** visitas orgánicas, lectura completa y reutilización por canal.

## Arquitectura de marca

- **Edward Jiménez:** interpretación, criterio, visión y tesis originales.
- **Agencia ProsperIA:** aplicación, evidencia operativa y acompañamiento empresarial.
- **PassportAI:** acceso práctico a capacidades de IA para usuarios no técnicos.
- **ProsperIA CRM:** continuidad comercial y gestión de relaciones.
- **PassportAI Leads:** complemento beta separado; no se presenta como parte incluida.
- **SVE90 Enterprise:** oferta empresarial separada.

## Las cinco rutas

1. **Radar de Disrupción:** qué señal merece atención.
2. **Criterio de Edward:** qué significa y qué decisión abre. Requiere aprobación de Edward.
3. **Inteligencia para Clínicas:** aplicación prioritaria en clínicas capilares, dentales y estéticas.
4. **Laboratorio ProsperIA:** aprendizajes verificables de implementación, sin fabricar casos.
5. **Las 4 Inteligencias:** desarrollo intelectual progresivo del futuro libro.

## Flujo de publicación

1. Investigación con fuentes primarias o claramente identificadas.
2. Generación de un borrador sin firma personal automática.
3. Verificación de afirmaciones, enlaces, cifras y límites de la evidencia.
4. Revisión de voz, utilidad y alineación estratégica.
5. Aprobación explícita si el autor será Edward Jiménez.
6. Publicación en el sitio como fuente canónica.
7. Adaptación posterior a LinkedIn, X, YouTube y correo, enlazando al original.

El comando `editorial_workflow.py archivo.json --publish-check` impide aprobar artículos
sin fuentes, revisor o autorización de firma cuando corresponda.

Después de esa validación, `publish_editorial.py archivo.json` guarda la versión aprobada
en `content/editorial_published/` —la fuente versionada de metadatos y evidencia— y actualiza
SQLite como índice de lectura. El comando no realiza commit, push ni despliegue.

## Criterio de abandono

Replantear una ruta si después de 12 publicaciones consistentes no produce señales de
autoridad, distribución cualificada ni conversaciones comerciales atribuibles.
