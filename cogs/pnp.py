import discord
from discord.ext import commands
from discord import app_commands
import random
import re

# Parameters
MAX_REROLLS = 5
MAX_FOOTER_LENGTH = 2048
INVISIBLE_MARKER = "\u200b"

# Dice Roller
def roll_pnp_dice(dice_number: int):
    if dice_number <= 0: return [], 0, []
    rolls, successes, sixes_values = [], 0, []
    for _ in range(dice_number):
        roll = random.randint(1, 6)
        rolls.append(roll)
        if roll == 2 or roll == 4:
            successes += 1
        elif roll == 6:
            successes += 2
            sixes_values.append(roll)
    return rolls, successes, sixes_values


def roll_explosion_dice(num_dice_to_start: int):
    if num_dice_to_start <= 0: return [], 0
    all_explosion_rolls, total_explosion_successes, dice_to_roll_now = [], 0, num_dice_to_start
    while dice_to_roll_now > 0:
        sixes_this_round = 0
        for _ in range(dice_to_roll_now):
            roll = random.randint(1, 6)
            all_explosion_rolls.append(roll)
            if roll == 2 or roll == 4:
                total_explosion_successes += 1
            elif roll == 6:
                total_explosion_successes += 2
                sixes_this_round += 1
        dice_to_roll_now = sixes_this_round
    return all_explosion_rolls, total_explosion_successes


# Formatting
def format_dice_list(rolls: list[int]) -> str:
    if not rolls: return ""
    return ', '.join([f"**{r}**" if r in (2, 4, 6) else str(r) for r in rolls])


def format_dice_list_for_footer(rolls: list[int]) -> str:
    if not rolls: return ""
    return ', '.join([str(r) for r in rolls])


# State Parsing
def parse_state_from_embed(embed: discord.Embed) -> dict:
    """Parses the embed to reconstruct the roll state."""
    state = {
        "reroll_count": 0,
        "has_ever_exploded": False,
        "current_rolls": [],
        "current_successes": 0,
        "initial_dice_number": 0,
        "roll_description": None
    }

    # Use the invisible marker in the footer for explosion memory
    if embed.footer and embed.footer.text:
        state["has_ever_exploded"] = INVISIBLE_MARKER in embed.footer.text

    if embed.description:
        first_line = embed.description.split('\n')[0]
        description_to_parse = first_line

        reroll_matches = re.findall(r"\(Re-roll #(\d+)\)", description_to_parse)
        if reroll_matches:
            state["reroll_count"] = max([int(m) for m in reroll_matches])
            description_to_parse = re.sub(r"\(Re-roll #\d+\)", "", description_to_parse).strip()

        match_desc = re.search(r"\((.*?)\)$", description_to_parse)
        if match_desc:
            state["roll_description"] = match_desc.group(1)

        match_dice = re.search(r"rolled (\d+) dice", first_line)
        if match_dice:
            state["initial_dice_number"] = int(match_dice.group(1))

        result_lines = [line for line in embed.description.split('\n') if "Result:" in line]
        if result_lines:
            last_result_line = result_lines[-1]
            rolls_str = re.findall(r'\d+', last_result_line)
            state["current_rolls"] = [int(r) for r in rolls_str]

    current_successes = 0
    for r in state["current_rolls"]:
        if r in (2, 4):
            current_successes += 1
        elif r == 6:
            current_successes += 2
    state["current_successes"] = current_successes

    return state


# Embed Formatting
def format_roll_embed(
        user: discord.User,
        action: str,
        dice_number: int,
        base_rolls: list[int],
        total_successes: int,
        reroll_count: int = 0,
        explosion_details: dict = None,
        roll_description: str = None,
        previous_history_str: str = "",
        has_ever_exploded: bool = False
) -> discord.Embed:
    title = f"{total_successes} Success{'es' if total_successes != 1 else ''}"
    description_parts = []
    color = discord.Color.default()
    desc_text = f" ({roll_description})" if roll_description else ""

    def get_result_str(rolls):
        return format_dice_list(rolls) or "None"

    if action == "Rolled":
        description_parts.append(f"{user.display_name} rolled {dice_number} dice!{desc_text}")
        description_parts.append(f"Result: {get_result_str(base_rolls)}")
        if explosion_details and explosion_details.get('rolls'):
            description_parts.append(f"Exploded Result: {get_result_str(explosion_details['rolls'])}")
            color = discord.Color.red()
    elif action == "Re-rolled":
        description_parts.append(
            f"{user.display_name} re-rolled {dice_number} dice! (Re-roll #{reroll_count}){desc_text}")
        description_parts.append(f"Result: {get_result_str(base_rolls)}")
        if explosion_details and explosion_details.get('rolls'):
            description_parts.append(f"Exploded Result: {get_result_str(explosion_details['rolls'])}")
        color = discord.Color.blue()

    embed = discord.Embed(title=title, description="\n\n".join(description_parts), color=color)

    # Footer
    new_history_line = ""
    if action in ["Rolled", "Re-rolled"]:
        step_successes = 0
        for r in base_rolls:
            if r in (2, 4):
                step_successes += 1
            elif r == 6:
                step_successes += 2

        footer_explosion_rolls = []
        if explosion_details:
            step_successes += explosion_details.get('successes', 0)
            footer_explosion_rolls = explosion_details.get('rolls', [])

        success_str = f"{step_successes} Success{'es' if step_successes != 1 else ''}"
        rolls_str = format_dice_list_for_footer(base_rolls + footer_explosion_rolls)
        action_str = f"Re-roll #{reroll_count}" if reroll_count > 0 else "Initial Roll"
        new_history_line = f"{action_str}: {success_str} ({rolls_str or 'None'})"

    full_history = previous_history_str
    if new_history_line:
        if full_history:
            full_history += "\n" + new_history_line
        else:
            full_history = new_history_line

    if full_history:
        footer_text = f"History:\n{full_history}"
        if has_ever_exploded:
            footer_text += INVISIBLE_MARKER

        if len(footer_text) > MAX_FOOTER_LENGTH:
            ellipsis = "\n..."
            allowed_len = MAX_FOOTER_LENGTH - len(ellipsis)
            footer_text = footer_text[-allowed_len:]
            first_newline = footer_text.find('\n')
            if first_newline != -1:
                footer_text = footer_text[first_newline + 1:]
            footer_text = "History:\n..." + footer_text
        embed.set_footer(text=footer_text)
    return embed


# Persistent Interactions
class PnPInteractionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def _handle_reroll(self, interaction: discord.Interaction):
        state = parse_state_from_embed(interaction.message.embeds[0])

        if state["reroll_count"] >= MAX_REROLLS:
            await interaction.response.send_message("You have reached the maximum number of re-rolls.", ephemeral=True)
            return

        reroll_count = state["reroll_count"] + 1
        base_rolls, base_successes, base_sixes = roll_pnp_dice(state["initial_dice_number"])
        explosion_details = None

        if state["has_ever_exploded"] and base_sixes:
            explosion_rolls, explosion_successes = roll_explosion_dice(len(base_sixes))
            explosion_details = {
                'rolls': explosion_rolls,
                'successes': explosion_successes,
                'initial_sixes_count': len(base_sixes)
            }

        is_exploded_state = state["has_ever_exploded"] or bool(explosion_details)

        title_successes = base_successes + (explosion_details['successes'] if explosion_details else 0)

        previous_history = ""
        if interaction.message.embeds[0].footer and interaction.message.embeds[0].footer.text:
            previous_history = interaction.message.embeds[0].footer.text.replace("History:\n", "").replace(
                INVISIBLE_MARKER, "")

        embed = format_roll_embed(
            user=interaction.user,
            action="Re-rolled",
            dice_number=state["initial_dice_number"],
            base_rolls=base_rolls,
            total_successes=title_successes,  # Pass the action-specific successes
            reroll_count=reroll_count,
            explosion_details=explosion_details,
            roll_description=state["roll_description"],
            previous_history_str=previous_history,
            has_ever_exploded=is_exploded_state
        )

        view = self
        view.update_buttons(base_rolls, reroll_count, is_currently_exploded=bool(explosion_details))
        await interaction.response.edit_message(embed=embed, view=view)

    async def _handle_explode(self, interaction: discord.Interaction):
        state = parse_state_from_embed(interaction.message.embeds[0])
        sixes_to_explode = [r for r in state["current_rolls"] if r == 6]

        if not sixes_to_explode:
            await interaction.response.defer()
            return

        explosion_rolls, explosion_successes = roll_explosion_dice(len(sixes_to_explode))

        title_successes = state["current_successes"] + explosion_successes

        explosion_details = {
            'rolls': explosion_rolls,
            'successes': explosion_successes,
            'initial_sixes_count': len(sixes_to_explode)
        }

        history_for_regen = ""
        if interaction.message.embeds[0].footer and interaction.message.embeds[0].footer.text:
            footer_text = interaction.message.embeds[0].footer.text.replace("History:\n", "").replace(INVISIBLE_MARKER,
                                                                                                      "")
            history_lines = footer_text.split('\n')
            if history_lines: history_lines.pop()
            history_for_regen = "\n".join(history_lines)

        original_action = "Re-rolled" if state["reroll_count"] > 0 else "Rolled"

        embed = format_roll_embed(
            user=interaction.user,
            action=original_action,
            dice_number=state["initial_dice_number"],
            base_rolls=state["current_rolls"],
            total_successes=title_successes,  # Pass the action-specific successes
            reroll_count=state["reroll_count"],
            explosion_details=explosion_details,
            roll_description=state["roll_description"],
            previous_history_str=history_for_regen,
            has_ever_exploded=True
        )

        view = self
        view.update_buttons(state["current_rolls"], state["reroll_count"], is_currently_exploded=True)
        await interaction.response.edit_message(embed=embed, view=view)

    def update_buttons(self, current_rolls: list, reroll_count: int, is_currently_exploded: bool):
        sixes = [r for r in current_rolls if r == 6]

        if reroll_count >= MAX_REROLLS:
            self.reroll_button.disabled = True
            self.reroll_button.label = "Re-roll (Max)"
        else:
            self.reroll_button.disabled = False
            self.reroll_button.label = "Re-roll"

        if sixes and not is_currently_exploded:
            self.explode_button.disabled = False
            self.explode_button.label = f"Explode {len(sixes)} Sixes"
        else:
            self.explode_button.disabled = True
            self.explode_button.label = "Exploded" if is_currently_exploded else "Explode 6s"

    @discord.ui.button(label="Re-roll", style=discord.ButtonStyle.primary, custom_id="pnp_persistent_reroll")
    async def reroll_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_reroll(interaction)

    @discord.ui.button(label="Explode 6s", style=discord.ButtonStyle.danger, custom_id="pnp_persistent_explode")
    async def explode_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_explode(interaction)


# --- Cog Definition ---
class PnPRollerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Rolls dice for Prowlers & Paragons: Ultimate Edition")
    @app_commands.describe(
        dice_number="The number of d6s to roll (1-100)",
        description="Optional description for the roll (e.g. 'Blast Attack')"
    )
    async def pnp_roll(self, interaction: discord.Interaction, dice_number: app_commands.Range[int, 1, 100],
                       description: str = None):
        """Rolls dice with persistent re-roll/explode options."""
        rolls, successes, sixes_values = roll_pnp_dice(dice_number)

        embed = format_roll_embed(
            user=interaction.user,
            action="Rolled",
            dice_number=dice_number,
            base_rolls=rolls,
            total_successes=successes,
            roll_description=description,
            has_ever_exploded=False
        )

        view = PnPInteractionView()
        view.update_buttons(rolls, reroll_count=0, is_currently_exploded=False)
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(PnPRollerCog(bot))
    bot.add_view(PnPInteractionView())
    print("PnP Roller Cog loaded and persistent view registered.")