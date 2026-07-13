import os
import json
import discord
from discord import app_commands
from discord.ext import commands

# Le token est récupéré depuis les variables d'environnement (à définir sur Discloud)
TOKEN = os.getenv("TOKEN")

DATA_FILE = "tasks.json"

STATUS_EMOJIS = {
    "rouge": "🔴",
    "orange": "🟠",
    "vert": "🟢",
}

STATUS_LABELS = {
    "rouge": "À faire",
    "orange": "En cours",
    "vert": "Terminée",
}


# ---------- Gestion des données ----------

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tasks": {}, "next_id": 1}


def save_tasks(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


data = load_tasks()


# ---------- Bot ----------

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def build_embed():
    embed = discord.Embed(
        title="📋 Liste des tâches",
        color=discord.Color.dark_blue(),
    )

    tasks = data["tasks"]
    if not tasks:
        embed.description = "Aucune tâche pour le moment. Utilise `/add` pour en créer une !"
    else:
        for task_id, task in sorted(tasks.items(), key=lambda x: int(x[0])):
            emoji = STATUS_EMOJIS.get(task["status"], "🔴")
            label = STATUS_LABELS.get(task["status"], "À faire")
            embed.add_field(
                name=f"#{task_id} — {emoji} {label}",
                value=task["description"],
                inline=False,
            )

    embed.set_footer(text=f"{len(tasks)} tâche(s) au total")
    return embed


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} commande(s) synchronisée(s).")
    except Exception as e:
        print(f"Erreur de synchronisation : {e}")
    print(f"Connecté en tant que {bot.user} (ID: {bot.user.id})")


@bot.tree.command(name="add", description="Ajouter une nouvelle tâche à la liste")
@app_commands.describe(description="Description de la tâche")
async def add(interaction: discord.Interaction, description: str):
    task_id = str(data["next_id"])
    data["tasks"][task_id] = {"description": description, "status": "rouge"}
    data["next_id"] += 1
    save_tasks(data)
    await interaction.response.send_message(embed=build_embed())


@bot.tree.command(name="delete", description="Supprimer une tâche par son ID")
@app_commands.describe(id="ID de la tâche à supprimer")
async def delete(interaction: discord.Interaction, id: str):
    if id in data["tasks"]:
        del data["tasks"][id]
        save_tasks(data)
        await interaction.response.send_message(embed=build_embed())
    else:
        await interaction.response.send_message(
            f"❌ Tâche #{id} introuvable.", ephemeral=True
        )


@bot.tree.command(name="vert", description="Marquer une tâche comme terminée 🟢")
@app_commands.describe(id="ID de la tâche")
async def vert(interaction: discord.Interaction, id: str):
    if id in data["tasks"]:
        data["tasks"][id]["status"] = "vert"
        save_tasks(data)
        await interaction.response.send_message(embed=build_embed())
    else:
        await interaction.response.send_message(
            f"❌ Tâche #{id} introuvable.", ephemeral=True
        )


@bot.tree.command(name="orange", description="Marquer une tâche comme en cours 🟠")
@app_commands.describe(id="ID de la tâche")
async def orange(interaction: discord.Interaction, id: str):
    if id in data["tasks"]:
        data["tasks"][id]["status"] = "orange"
        save_tasks(data)
        await interaction.response.send_message(embed=build_embed())
    else:
        await interaction.response.send_message(
            f"❌ Tâche #{id} introuvable.", ephemeral=True
        )


@bot.tree.command(name="rouge", description="Remettre une tâche à 'à faire' 🔴")
@app_commands.describe(id="ID de la tâche")
async def rouge(interaction: discord.Interaction, id: str):
    if id in data["tasks"]:
        data["tasks"][id]["status"] = "rouge"
        save_tasks(data)
        await interaction.response.send_message(embed=build_embed())
    else:
        await interaction.response.send_message(
            f"❌ Tâche #{id} introuvable.", ephemeral=True
        )


@bot.tree.command(name="liste", description="Afficher la liste des tâches")
async def liste(interaction: discord.Interaction):
    await interaction.response.send_message(embed=build_embed())


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError(
            "Aucun TOKEN trouvé. Ajoute la variable d'environnement TOKEN."
        )
    bot.run(TOKEN)
