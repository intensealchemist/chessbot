import chess
import chess.engine

def test_ai_move():
    board = chess.Board()
    engine_path = "/usr/games/stockfish"  # Adjust this path based on your setup

    try:
        with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
            # Set the skill level
            engine.configure({"Skill Level": 5})
            
            # Make a move
            result = engine.play(board, chess.engine.Limit(time=2.0))
            print("AI Move:", result.move)
            
            # Push the move to the board
            if result.move in board.legal_moves:
                board.push(result.move)
                print("Board after AI move:")
                print(board)
            else:
                print("Generated move was not legal.")
    except Exception as e:
        print(f"Error: {e}")

test_ai_move()
