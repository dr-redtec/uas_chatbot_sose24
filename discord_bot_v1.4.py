import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging
import subprocess
import asyncio

# Lade Umgebungsvariablen aus der .env Datei
load_dotenv()

# Konfiguriere das Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_bot.log'),  # Logs werden in dieser Datei gespeichert
        logging.StreamHandler()  # Logs werden weiterhin auch auf der Konsole ausgegeben
    ]
)
logger = logging.getLogger('discord_bot')

# Bot-Token und Guild-ID aus Umgebungsvariablen laden
bot_token = os.getenv('DISCORD_BOT_TOKEN')
allowed_guild_id = int(os.getenv('ALLOWED_GUILD_ID'))

# Erstelle ein Intents-Objekt und aktiviere die benötigten Intents
intents = discord.Intents.default()
intents.message_content = True  # Ermöglicht den Zugriff auf Nachrichteninhalte

# Erstelle ein Bot-Objekt mit den spezifizierten Intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Event, das ausgeführt wird, wenn der Bot sich mit Discord verbindet
@bot.event
async def on_ready():
    logger.info(f'Bot ist eingeloggt als {bot.user}')
    logger.info('Bot ist aktiv auf folgenden Servern:')
    for guild in bot.guilds:
        logger.info(f'- {guild.name} (ID: {guild.id})')

# Überprüfe, ob der Bot in einer erlaubten Gilde (Server) ist
@bot.event
async def on_guild_join(guild):
    if guild.id != allowed_guild_id:
        await guild.leave()
        logger.warning(f'Bot hat den unerlaubten Server {guild.name} (ID: {guild.id}) verlassen.')

# Definiere den Befehl !hallo
@bot.command()
async def hallo(ctx):
    if ctx.guild.id == allowed_guild_id:
        await ctx.send('Hallo!')
        logger.info(f'Befehl !hallo wurde von {ctx.author} im Channel {ctx.channel} auf dem Server {ctx.guild.name} ausgeführt.')
    else:
        await ctx.send('Dieser Bot ist nicht für diesen Server zugelassen.')
        logger.warning(f'Unerlaubter Serverzugriff von {ctx.guild.name} (ID: {ctx.guild.id}).')

# Definiere den Befehl !simple
@bot.command()
async def simple(ctx, *, query_text: str):
    if ctx.guild.id == allowed_guild_id:
        await ctx.send('Deine Frage wird bearbeitet, bitte einen Moment...')
        try:
            # Starte das Skript und warte auf das Ergebnis
            result = await asyncio.to_thread(run_simple_rag, query_text)
            await ctx.send(f'Antwort: {result}')
            logger.info(f'Frage von {ctx.author}: {query_text}')
            logger.info(f'Antwort: {result}')
            logger.info(f'Befehl !simple wurde von {ctx.author} im Channel {ctx.channel} auf dem Server {ctx.guild.name} ausgeführt.')
        except Exception as e:
            logger.error(f'Fehler beim Ausführen der Abfrage: {str(e)}')
            await ctx.send('Es gab ein Problem bei der Verarbeitung deiner Anfrage.')
    else:
        await ctx.send('Dieser Bot ist nicht für diesen Server zugelassen.')
        logger.warning(f'Unerlaubter Serverzugriff von {ctx.guild.name} (ID: {ctx.guild.id}).')
# Definiere den Befehl !context
@bot.command()
async def context(ctx, *, query_text: str):
    if ctx.guild.id == allowed_guild_id:
        await ctx.send('Deine Frage wird bearbeitet, bitte einen Moment...')
        try:
            # Starte das Skript und warte auf das Ergebnis
            result = await asyncio.to_thread(run_context_rag, query_text)
            await ctx.send(f'Antwort: {result}')
            logger.info(f'Frage von {ctx.author}: {query_text}')
            logger.info(f'Antwort: {result}')
            logger.info(f'Befehl !context wurde von {ctx.author} im Channel {ctx.channel} auf dem Server {ctx.guild.name} ausgeführt.')
        except Exception as e:
            logger.error(f'Fehler beim Ausführen der Abfrage: {str(e)}')
            await ctx.send('Es gab ein Problem bei der Verarbeitung deiner Anfrage.')
    else:
        await ctx.send('Dieser Bot ist nicht für diesen Server zugelassen.')
        logger.warning(f'Unerlaubter Serverzugriff von {ctx.guild.name} (ID: {ctx.guild.id}).')
# Definiere den Befehl !transform_simple
@bot.command()
async def transform_simple(ctx, *, query_text: str):
    if ctx.guild.id == allowed_guild_id:
        await ctx.send('Deine Frage wird bearbeitet, bitte einen Moment...')
        try:
            # Starte das Skript und warte auf das Ergebnis
            result = await asyncio.to_thread(run_transform_simple_rag, query_text)
            await ctx.send(f'Antwort: {result}')
            logger.info(f'Frage von {ctx.author}: {query_text}')
            logger.info(f'Antwort: {result}')
            logger.info(f'Befehl !transform_simple wurde von {ctx.author} im Channel {ctx.channel} auf dem Server {ctx.guild.name} ausgeführt.')
        except Exception as e:
            logger.error(f'Fehler beim Ausführen der Abfrage: {str(e)}')
            await ctx.send('Es gab ein Problem bei der Verarbeitung deiner Anfrage.')
    else:
        await ctx.send('Dieser Bot ist nicht für diesen Server zugelassen.')
        logger.warning(f'Unerlaubter Serverzugriff von {ctx.guild.name} (ID: {ctx.guild.id}).')
# Definiere den Befehl !transform_context        
@bot.command()
async def transform_context(ctx, *, query_text: str):
    if ctx.guild.id == allowed_guild_id:
        await ctx.send('Deine Frage wird bearbeitet, bitte einen Moment...')
        try:
            # Starte das Skript und warte auf das Ergebnis
            result = await asyncio.to_thread(run_transform_context_rag, query_text)
            await ctx.send(f'Antwort: {result}')
            logger.info(f'Frage von {ctx.author}: {query_text}')
            logger.info(f'Antwort: {result}')
            logger.info(f'Befehl !transform_context wurde von {ctx.author} im Channel {ctx.channel} auf dem Server {ctx.guild.name} ausgeführt.')
        except Exception as e:
            logger.error(f'Fehler beim Ausführen der Abfrage: {str(e)}')
            await ctx.send('Es gab ein Problem bei der Verarbeitung deiner Anfrage.')
    else:
        await ctx.send('Dieser Bot ist nicht für diesen Server zugelassen.')
        logger.warning(f'Unerlaubter Serverzugriff von {ctx.guild.name} (ID: {ctx.guild.id}).')

# Definiere den Befehl !simple_hessisch   
# EASTEREGG     
@bot.command()
async def simple_hessisch(ctx, *, query_text: str):
    if ctx.guild.id == allowed_guild_id:
        await ctx.send('Deine Frage wird bearbeitet, bitte einen Moment...')
        try:
            # Starte das Skript und warte auf das Ergebnis
            result = await asyncio.to_thread(run_simple_hessisch, query_text)
            await ctx.send(f'Antwort: {result}')
            logger.info(f'Frage von {ctx.author}: {query_text}')
            logger.info(f'Antwort: {result}')
            logger.info(f'Befehl !transform_context wurde von {ctx.author} im Channel {ctx.channel} auf dem Server {ctx.guild.name} ausgeführt.')
        except Exception as e:
            logger.error(f'Fehler beim Ausführen der Abfrage: {str(e)}')
            await ctx.send('Es gab ein Problem bei der Verarbeitung deiner Anfrage.')
    else:
        await ctx.send('Dieser Bot ist nicht für diesen Server zugelassen.')
        logger.warning(f'Unerlaubter Serverzugriff von {ctx.guild.name} (ID: {ctx.guild.id}).')

def run_simple_rag(query_text):
    try:
        # Importiere die Funktion query_rag aus dem proto_query_v1 Skript
        from query_simple_rag import start_query
        # Führe die Abfrage aus und gib das Ergebnis zurück
        return start_query(query_text)
    except Exception as e:
        # Fehler unterdrücken und None zurückgeben
        logger.error(f'Fehler beim Ausführen der proto_query: {str(e)}')
        return 'Es gab einen Fehler bei der Verarbeitung deiner Anfrage.'
    
def run_context_rag(query_text):
    try:
        # Importiere die Funktion query_rag aus dem proto_query_v1 Skript
        from context_enrichment_rag import start_query_context
        # Führe die Abfrage aus und gib das Ergebnis zurück
        return start_query_context(query_text)
    except Exception as e:
        # Fehler unterdrücken und None zurückgeben
        logger.error(f'Fehler beim Ausführen der proto_query: {str(e)}')
        return 'Es gab einen Fehler bei der Verarbeitung deiner Anfrage.'

def run_transform_simple_rag(query_text):
    try:
        # Importiere die Funktion query_rag aus dem proto_query_v1 Skript
        from query_transformation_simple_rag import start_for_bot
        # Führe die Abfrage aus und gib das Ergebnis zurück
        return start_for_bot(query_text)
    except Exception as e:
        # Fehler unterdrücken und None zurückgeben
        logger.error(f'Fehler beim Ausführen der proto_query: {str(e)}')
        return 'Es gab einen Fehler bei der Verarbeitung deiner Anfrage.'
    
def run_transform_context_rag(query_text):
    try:
        # Importiere die Funktion query_rag aus dem proto_query_v1 Skript
        from query_transformation_context_rag import start_for_bot
        # Führe die Abfrage aus und gib das Ergebnis zurück
        return start_for_bot(query_text)
    except Exception as e:
        # Fehler unterdrücken und None zurückgeben
        logger.error(f'Fehler beim Ausführen der proto_query: {str(e)}')
        return 'Es gab einen Fehler bei der Verarbeitung deiner Anfrage.'

def run_simple_hessisch(query_text):
    try:
        # Importiere die Funktion query_rag aus dem proto_query_v1 Skript
        from query_simple_rag import start_query
        from llms import initialize_models, ask_llm_with_ollama_on_hessisch
        # Führe die Abfrage aus und gib das Ergebnis zurück
        mistral_model, llama_model = initialize_models()
        org_anwser = start_query(query_text)
        return ask_llm_with_ollama_on_hessisch(org_anwser, mistral_model)
    except Exception as e:
        # Fehler unterdrücken und None zurückgeben
        logger.error(f'Fehler beim Ausführen der proto_query: {str(e)}')
        return 'Es gab einen Fehler bei der Verarbeitung deiner Anfrage.'
    

# Starte den Bot mit deinem Token
bot.run(bot_token)