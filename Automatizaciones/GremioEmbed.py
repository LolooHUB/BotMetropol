# ================= READY =================
    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(self.CANAL_ANUNCIOS_ID)
        if not channel:
            return

        # --- LÓGICA PARA EVITAR DUPLICADOS ---
        # Buscamos en la colección 'Configuracion' si ya enviamos el mensaje
        config_ref = self.db.collection("Configuracion").document("gremio_msg")
        doc = config_ref.get()

        if doc.exists:
            # Si el documento existe, el mensaje ya fue enviado.
            # Opcional: Podrías buscar el mensaje y editarlo, pero por ahora 
            # simplemente retornamos para no enviarlo de nuevo.
            return

        # Si no existe, procedemos a enviarlo
        hora_arg = datetime.datetime.now(
            ZoneInfo("America/Argentina/Buenos_Aires")
        ).strftime("%H:%M")

        embed = discord.Embed(
            title="🚌 Gremio de Colectiveros | La Nueva Metropol S.A.",
            description=(
                "Bienvenido al espacio de representación oficial de los conductores. "
                "Este gremio ha sido constituido para velar por los derechos, la seguridad "
                "y el bienestar de todo el personal operativo de la empresa.\n\n"
                
                "### 📌 ¿Cuál es nuestro propósito?\n"
                "El gremio actúa como el nexo principal entre el cuerpo de conductores y la dirección. "
                "Nuestra misión es garantizar un entorno de trabajo justo, coordinar la asistencia "
                "ante eventualidades en ruta y profesionalizar nuestro servicio mediante la unión.\n\n"
                
                "### 🛠️ Beneficios y Funciones\n"
                "* **Defensa Laboral:** Representación activa ante sanciones o conflictos.\n"
                "* **Canal de Reclamos:** Espacio formal para reportar el estado de las unidades o problemas en terminales.\n"
                "* **Organización Operativa:** Coordinación de medidas de fuerza, asambleas y comunicados de último momento.\n"
                "* **Apoyo entre Colegas:** Red de contacto directa para asistencia en incidentes viales o mecánicos.\n\n"
                
                "### 🏛️ Estructura Orgánica\n"
                f"• **Cuerpo Directivo:** <@&{self.ROL_DIRECTIVOS_ID}> (Gestión y toma de decisiones)\n"
                f"• **Cuerpo de Delegados:** Conductores activos con voz y voto en la asamblea.\n"
                f"• **Afiliados:** <@&{self.ROL_GREMIO_ID}> (Personal con acceso a canales exclusivos).\n\n"
                
                "### 💬 Comunicación Oficial\n"
                f"Para debates, consultas y reportes diarios, utilizá el canal: <#{self.CANAL_COMUNICACION_ID}>\n\n"
                "--- \n"
                "*Al unirte, te comprometés a respetar el reglamento interno y a actuar bajo los valores de compañerismo del gremio.*"
            ),
            color=0x1F8B4C
        )

        embed.set_footer(
            text=f"La Nueva Metropol S.A. | {hora_arg}"
        )

        try:
            file = discord.File(self.BANNER_PATH, filename="BannerGremio.png")
            embed.set_image(url="attachment://BannerGremio.png")

            mensaje = await channel.send(
                embed=embed,
                view=self.GremioView(self),
                file=file
            )

            # Guardamos el ID en Firestore para que la próxima vez sepa que ya existe
            config_ref.set({
                "message_id": mensaje.id,
                "channel_id": channel.id,
                "fecha_creacion": hora_arg
            })
            
        except FileNotFoundError:
            print(f"Error: No se encontró el banner en {self.BANNER_PATH}")
            # Si falla el archivo, enviamos sin imagen para no romper el flujo
            mensaje = await channel.send(embed=embed, view=self.GremioView(self))
            config_ref.set({"message_id": mensaje.id, "channel_id": channel.id})
