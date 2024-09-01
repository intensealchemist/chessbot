import os
import discord
from discord.ext import commands
import chess
import chess.svg
import chess.engine
from PIL import Image
from cairosvg import svg2png

# Initialize bot with command prefix and intents
intents = discord.Intents.default()
intents.message_content = True  # Ensure Message Content Intent is enabled
bot = commands.Bot(command_prefix="!", intents=intents)

# Load environment variable for bot token
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Global variables to track game state
board = chess.Board()
mode = None

# Function to generate and save the board image
def generate_board_image():
    # Generate SVG representation of the board
    board_svg = chess.svg.board(board=board, size=350)  # Adjust size as needed
    # Convert SVG to PNG
    svg2png(bytestring=board_svg.encode('utf-8'), write_to='chessboard.png')

# Command to select game mode
@bot.command(name='mode')
async def select_mode(ctx, choice: str):
    global mode
    if choice.lower() not in ['solo', 'ai']:
        await ctx.send("Invalid mode. Choose `solo` or `ai`.")
        return
    
    mode = choice.lower()
    await ctx.send(f"Mode set to `{mode}`. Now use `!start` to begin the game.")

# Command to start a new chess game
@bot.command(name='start')
async def start_game(ctx):
    global board, mode
    if mode is None:
        await ctx.send("Please select a mode using `!mode solo` or `!mode ai`.")
        return

    board.reset()
    generate_board_image()
    await ctx.send(f"New chess game started in `{mode}` mode!", file=discord.File("chessboard.png"))

# Command to make a move
@bot.command(name='move')
async def make_move(ctx, move: str):
    global board, mode
    if mode is None:
        await ctx.send("Please select a mode using `!mode solo` or `!mode ai`.")
        return

    try:
        move_obj = chess.Move.from_uci(move)
        if move_obj in board.legal_moves:
            board.push(move_obj)
            generate_board_image()
            await ctx.send(f"Move `{move}` accepted.", file=discord.File("chessboard.png"))
            if mode == 'ai' and not board.is_game_over():
                await ai_move(ctx)  # AI makes a move after the player
        else:
            await ctx.send("Invalid move. Try again.")
    except ValueError:
        await ctx.send("Invalid move format. Use UCI format like `e2e4`.")

# Command to let AI make a move
@bot.command(name='ai')
async def ai_move(ctx):
    global board
    if board.is_game_over():
        await ctx.send("Game over!")
        return
    try:
        engine = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
    except FileNotFoundError:
        await ctx.send("Stockfish engine not found. Please install it using `sudo apt-get install stockfish`.")
        return

    try:
        result = engine.play(board, chess.engine.Limit(time=1.0))
        board.push(result.move)
        generate_board_image()
        await ctx.send(f"AI plays `{result.move}`.", file=discord.File("chessboard.png"))
    except Exception as e:
        await ctx.send(f"Error with AI move: {e}")
    finally:
        engine.quit()

# Command to exit the game
@bot.command(name='exit')
async def exit_game(ctx):
    await ctx.send("Exiting the game. Bye!")
    await bot.logout()

# Run the bot
if TOKEN is None:
    print("Error: DISCORD_BOT_TOKEN environment variable not set.")
else:
    bot.run(TOKEN)
