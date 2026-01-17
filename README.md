# 🚌 MetropolBot - Central de Operaciones

¡Bienvenido al repositorio del bot oficial de **La Nueva Metropol S.A.**! Este bot está diseñado exclusivamente para gestionar nuestra comunidad de simulación en Roblox, facilitando el trabajo de los directivos y la asistencia a nuestros choferes en calle.

---

## 🚀 Funciones Principales

### 🛡️ Moderación (Uso Administrativo)
El bot utiliza **Modales** (ventanas emergentes) para que el equipo de Directivos y Personal pueda aplicar sanciones de forma ordenada. 

* **Baneos y Kicks:** Al ejecutar `/ban` o `/kick`, se abre una ventana para completar el motivo, la duración y adjuntar pruebas. Al terminar, el bot genera un reporte automático con el sello de la empresa.
* **Sistema de Warns:** Controlamos las faltas de los usuarios. Cada usuario puede acumular hasta 3 advertencias antes de que se tomen medidas mayores. Todo queda registrado con fecha y hora.

### 🔧 Auxilio Mecánico y Siniestros
Para los choferes que están en servicio y tienen algún inconveniente en el mapa:
* Usa el comando `/auxilio` (solo si no eres Cliente).
* Deberás indicar quién conduce, dónde estás y qué pasó, además de subir una foto del problema. 📸
* Esto envía una alerta inmediata a los **Auxiliares** para que salgan a pista a asistirte.

### 💬 Atención al Usuario y Consultas
El bot no es solo una herramienta de mando, también tiene "vida" propia:
* **Pings:** Si mencionas al bot, te va a responder con frases aleatorias sobre la empresa o recordándote si ya te anotaste en los formularios.
* **Comandos Rápidos:** Con `!ayuda` o `!formularios` el bot te manda la info necesaria de forma privada (efímera) para no llenar el chat de spam. 🔰

---

## 📁 Estructura del Proyecto
Para que el código no sea un lío, lo tenemos organizado así:
* `index.js`: El motor del bot y los estados (Playing...).
* `Comandos/`: Acá adentro está la lógica de cada comando por separado.
* `Imgs/`: Los logos y banners oficiales de la Metropol que usa el bot para los reportes.

---

## ⚙️ Notas para el Staff de Desarrollo
* **Seguridad:** El Token se maneja mediante **GitHub Secrets**. Si vas a testear algo localmente, usá un archivo `.env` y no lo subas nunca al repo. 🔐
* **Dependencias:** Usamos `discord.js` en su versión más reciente. No te olvides de hacer un `npm install` si clonás el proyecto.
* **Jerarquía:** Para que los comandos de moderación funcionen, el rol del bot siempre tiene que estar arriba de todo en los ajustes del servidor.

---
**La Nueva Metropol S.A.**
*Cumpliendo recorridos, uniendo comunidades.* 🇦🇷
