import sys
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from play_game import BaseGame, PlayDecorator
from player import HumanPlayer, HeuristicAI, RandomAI
from constants import DIRECTIONS, TIMESHIFT, ERAS

class BoardGameGUI:
    """This is the GUI class for the board game TTYKM"""
    def __init__(self, root, p1_type='human', p2_type='human', use_history=False, verbose=False):
        """Initiate the frame with the default settings"""
        self.root = root
        self.root.title("Board Game - That Time You Killed Me")
        
        self.p1 = self.create_player("white", p1_type)
        self.p2 = self.create_player("black", p2_type)
        self.game = BaseGame(self.p1, self.p2, current=0, use_history=use_history, verbose=verbose)
        self.game = PlayDecorator(self.game)
        
        self.selected_piece = None
        self.highlighted_moves = []
        self.cell_size = 60
        self.era_colors = {'past': '#E6D5B8', 'present': '#F0F0F0', 'future': '#B8D5E6'}

        self.actions_taken = 0
        self.max_actions = 2
        self.awaiting_command = False

        self.setup_ui()
        self.update_display()

        if not isinstance(self.game._game.current_player(), HumanPlayer):
            # messagebox.showinfo("Next Turn", f"Next turn: {self.game._game.current_player().color.capitalize()}")
            self.root.after(1000, self.ai_move)
    

    def create_player(self, color, ptype):
        """Helper function to create player based on the player type indicated"""
        if ptype == 'human': 
            return HumanPlayer(color)
        if ptype == 'random': 
            return RandomAI(color)
        if ptype == 'heuristic': 
            return HeuristicAI(color)
        raise ValueError("Unknown player type")

    def setup_ui(self):
        """Set up the initial UI: three boards with the pieces on the starting locations with required buttons set up"""
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.era_selector_frame = tk.Frame(self.root)
        self.era_selector_frame.pack(fill=tk.X)
        
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(pady=10)
        
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.p1_label = tk.Label(self.top_frame, text=f"Player 1 (White): {type(self.p1).__name__}", fg='black')
        self.p1_label.pack(side=tk.LEFT, padx=10)
        
        self.p2_label = tk.Label(self.top_frame, text=f"Player 2 (Black): {type(self.p2).__name__}", fg='black')
        self.p2_label.pack(side=tk.RIGHT, padx=10)
        
        self.setup_era_selector()

        self.create_boards()
        
        if self.game._game.caretaker:
            self.undo_btn = tk.Button(self.control_frame, text="Undo", command=self.undo_move)
            self.undo_btn.pack(side=tk.LEFT, padx=5)
            
            self.redo_btn = tk.Button(self.control_frame, text="Redo", command=self.redo_move)
            self.redo_btn.pack(side=tk.LEFT, padx=5)
        
            self.next_btn = tk.Button(self.control_frame, text="Next", command=self.next_move)
            self.next_btn.pack(side=tk.LEFT, padx=5)
        
        self.quit_btn = tk.Button(self.control_frame, text="Quit", command=self.root.quit)
        self.quit_btn.pack(side=tk.RIGHT, padx=5)

        self.status_label = tk.Label(self.root, text="", fg="blue", anchor="w")
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

    def setup_era_selector(self):
        """Create era selection controls for human players"""
        self.era_vars = {
            'white': tk.StringVar(value=self.game._game.focus['white']),
            'black': tk.StringVar(value=self.game._game.focus['black'])
        }
        
        tk.Label(self.era_selector_frame, text="White Focus:").grid(row=0, column=0, padx=5)
        self.white_era_menu = ttk.Combobox(
            self.era_selector_frame,
            textvariable=self.era_vars['white'],
            values=['past', 'present', 'future'],
            state='readonly'
        )
        self.white_era_menu.grid(row=0, column=1, padx=5)
        self.white_era_menu.bind('<<ComboboxSelected>>', lambda e: self.change_focus('white'))
        
        tk.Label(self.era_selector_frame, text="Black Focus:").grid(row=0, column=2, padx=5)
        self.black_era_menu = ttk.Combobox(
            self.era_selector_frame,
            textvariable=self.era_vars['black'],
            values=['past', 'present', 'future'],
            state='readonly'
        )
        self.black_era_menu.grid(row=0, column=3, padx=5)
        self.black_era_menu.bind('<<ComboboxSelected>>', lambda e: self.change_focus('black'))

    def change_focus(self, color):
        """Helper function to change the focus with UI update"""
        new_era = self.era_vars[color].get()
        self.game._game.focus[color] = new_era
        self.update_display()


    def create_boards(self):
        """Create the three era boards for inserting pieces"""
        self.era_frames = {}
        self.canvases = {}
        
        for i, era in enumerate(['past', 'present', 'future']):
            frame = tk.LabelFrame(self.board_frame, text=era.capitalize(), bg=self.era_colors[era])
            frame.grid(row=0, column=i, padx=10, pady=5)
            self.era_frames[era] = frame
            
            canvas = tk.Canvas(frame, width=4*self.cell_size, height=4*self.cell_size, 
                              bg=self.era_colors[era], highlightthickness=0)
            canvas.grid()
            self.canvases[era] = canvas
            
            for row in range(4):
                for col in range(4):
                    x1, y1 = col*self.cell_size, row*self.cell_size
                    x2, y2 = (col+1)*self.cell_size, (row+1)*self.cell_size
                    canvas.create_rectangle(x1, y1, x2, y2, outline='black', width=1)
            
            canvas.bind("<Button-1>", lambda e, era=era: self.on_canvas_click(e, era))


    def on_canvas_click(self, event, era):
        """Ensure providing response when the clicking in on the cell for pieces"""
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        if 0 <= row < 4 and 0 <= col < 4:
            self.on_cell_click(row, col, era)

    def draw_piece(self, canvas, row, col, color):
        """Draw a chess-like piece on the board using different shapes for different players"""
        x = col * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 3
        
        if color == 'white':
            canvas.create_oval(x-radius, y-radius, x+radius, y+radius, 
                             fill='white', outline='black', width=2, tags="piece")
        else:
            canvas.create_rectangle(x-radius, y-radius, x+radius, y+radius,
                                  fill='black', outline='white', width=2, tags="piece")

    def update_display(self):
        """Update the display of boards and pieces after each changes made by two players"""
        
        self.era_vars['white'].set(self.game._game.focus['white'])
        self.era_vars['black'].set(self.game._game.focus['black'])
        
        current_player = self.game._game.current_player()
        self.p1_label.config(font=('Arial', 10, 'bold' if current_player == self.p1 else 'normal'))
        self.p2_label.config(font=('Arial', 10, 'bold' if current_player == self.p2 else 'normal'))
        
        for era in ['past', 'present', 'future']:
            board = self.game._game.boards[era]
            canvas = self.canvases[era]
            
            canvas.delete("piece")
            canvas.delete("highlight")

            canvas.configure(bg='light yellow')
            self.root.after(100, lambda c=canvas, era=era: c.configure(bg=self.era_colors[era]))
            
            for row in range(4):
                for col in range(4):
                    piece = board.grid[row][col]
                    if piece:
                        self.draw_piece(canvas, row, col, piece.color)
            
            if self.selected_piece:
                sel_row, sel_col, sel_era = self.selected_piece
                if sel_era == era:
                    self.highlight_cell(canvas, sel_row, sel_col, 'yellow')
            
            for move in self.highlighted_moves:
                r, c, e = move
                if e == era:
                    self.highlight_cell(canvas, r, c, 'light green')
        
        for era, frame in self.era_frames.items():
            if era == self.game._game.focus['white'] or era == self.game._game.focus['black']:
                frame.config(highlightbackground='red', highlightthickness=2)
            else:
                frame.config(highlightbackground=self.era_colors[era], highlightthickness=1)
        

    
    def highlight_cell(self, canvas, row, col, color):
        """Highlight a cell on the canvas"""
        x1 = col * self.cell_size
        y1 = row * self.cell_size
        x2 = (col + 1) * self.cell_size
        y2 = (row + 1) * self.cell_size
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, stipple='gray50', tags="highlight")



    def on_cell_click(self, row, col, era):
        """Manage the Human player select and move the piece by clicking on the board"""
        current_player = self.game._game.current_player()
        if self.game._game.caretaker and not self.awaiting_command:
            self.set_status("Please click Undo, Redo, or Next before selecting.")
            return
        
        if not isinstance(current_player, HumanPlayer):
            return

        board = self.game._game.boards[era]
        piece = board.grid[row][col]
        current_focus_era = self.game._game.focus[current_player.color]

        if self.selected_piece is None:
            if era != current_focus_era:
                self.set_status(f"You can only select pieces in the {current_focus_era} era.")
                return
            current_player = self.game._game.current_player()
            current_focus = self.game._game.focus[current_player.color]
            still_has_piece = any(
                p for row in self.game._game.boards[current_focus].grid for p in row
                if p and p.color == current_player.color
            )
            if not still_has_piece:
                self.end_turn()
            
            if piece and piece.color == current_player.color:
                self.selected_piece = (row, col, era)
                self.highlighted_moves = self.get_available_moves(row, col, era)
                self.awaiting_command = True
                self.update_display()
        else:
            if (row, col, era) in self.highlighted_moves:
                self.execute_move(self.selected_piece, (row, col, era))
            else:
                self.selected_piece = None
                self.highlighted_moves = []
                self.update_display()


    def get_available_moves(self, row, col, era):
        """Get available moves for the selected piece"""
        piece = self.game._game.boards[era].get_piece(row, col)
        if not piece:
            return []
        
        moves = set()
        
        for direction in DIRECTIONS.keys():  
            if self.game._game.can_move(piece, direction):
                dx, dy = DIRECTIONS[direction]
                new_row, new_col = row + dx, col + dy
                if self.game._game.boards[era].is_within_bounds(new_row, new_col):
                    moves.add((new_row, new_col, era))
        
        for direction, dz in TIMESHIFT.items():  
            if self.game._game.can_move(piece, direction):
                new_era_idx = ERAS.index(era) + dz
                if 0 <= new_era_idx < len(ERAS):
                    new_era = ERAS[new_era_idx]
                    target_board = self.game._game.boards[new_era]
                    if target_board.grid[row][col] is None:
                        moves.add((row, col, new_era))
        
        return list(moves)

    def execute_move(self, from_pos, to_pos):
        """Move execution: UI is different here. As human player take two steps with board updating seperately """
        from_row, from_col, from_era = from_pos
        to_row, to_col, to_era = to_pos

        board = self.game._game.boards[from_era]
        piece = board.grid[from_row][from_col]
        if not piece:
            return

        if from_era == to_era:
            dx, dy = to_row - from_row, to_col - from_col
            direction = next((d for d, (ddx, ddy) in DIRECTIONS.items() if (dx, dy) == (ddx, ddy)), None)
        else:
            dz = ERAS.index(to_era) - ERAS.index(from_era)
            direction = next((d for d, ddz in TIMESHIFT.items() if dz == ddz), None)

        if direction:
            self.game._game.move_piece(piece, direction)

        self.selected_piece = None
        self.highlighted_moves = []

        focus_era = self.game._game.focus[self.game._game.current_player().color]
        still_has_piece = any(
            p for row in self.game._game.boards[focus_era].grid for p in row
            if p and p.color == self.game._game.current_player().color
        )

        if still_has_piece:
            self.actions_taken += 1
            if self.actions_taken >= self.max_actions:
                self.update_display()
                self.end_turn()
        else:
            self.update_display()
            self.end_turn()

    
    def end_turn(self):
        """Helper function to end the turn and switch player."""
        current_player = self.game._game.current_player()

        if isinstance(current_player, HumanPlayer):
        
            self.ask_focus_change(current_player)


        self.game._game.turn += 1
        self.game._game.current = 1 - self.game._game.current
        self.actions_taken = 0
        self.awaiting_command = False

        if self.game._game.is_winning_move(self.game._game.current_player()):
            winner = self.game._game.get_opponent().color
            self.show_winner(winner)
            return 

        next_player = self.game._game.current_player()
        messagebox.showinfo("Next Turn", f"Next turn: {next_player.color.capitalize()}")

        if not isinstance(self.game._game.current_player(), HumanPlayer):
            self.root.after(1000, self.ai_move)
    
    def ask_focus_change(self, player):
        """Take the focus choice option from the Human Player user"""
        old_focus = self.game._game.focus[player.color]
        eras = ['past', 'present', 'future']

        while True:
            selected_focus = simpledialog.askstring("Focus Selection", f"Current focus: {old_focus}. Choose a new focus (past, present, future):")
            if selected_focus is None:
                continue  
            selected_focus = selected_focus.lower()
            if selected_focus not in eras:
                messagebox.showerror("Invalid Era", "Please select 'past', 'present', or 'future'.")
                continue
            if selected_focus == old_focus:
                messagebox.showerror("Same Era", "You must select a DIFFERENT era than current focus.")
                continue
            break  

        self.game._game.focus[player.color] = selected_focus
        

    def ai_move(self):
        """Handle the moves for AI players: use the move strategy directly"""
        if not isinstance(self.game._game.current_player(), HumanPlayer):
            player = self.game._game.current_player()
            move = player.select_move(self.game._game)
            if move:
                move.apply(self.game._game)
                self.update_display()
                self.end_turn()


    def set_status(self, message):
        """Helper function to notify the actions taken, for example, the redo/undo/next has been clicked"""
        self.status_label.config(text=message)
        self.root.after(1500, lambda: self.status_label.config(text=""))


    def undo_move(self):
        """Undo the move and go back to previou turn"""
        if self.game._game.caretaker:
            old_turn = self.game._game.turn
            self.game._game.caretaker.undo()
            new_turn = self.game._game.turn
            self.selected_piece = None
            self.highlighted_moves = []
            self.actions_taken = 0
            self.update_display()
            self.set_status(f"Undo: Reverted from turn {old_turn} to turn {new_turn}")
            self.awaiting_command = True

    def redo_move(self):
        """Redo the move and go to the next turn saved in the future"""
        if self.game._game.caretaker:
            old_turn = self.game._game.turn
            self.game._game.caretaker.redo()
            new_turn = self.game._game.turn
            self.selected_piece = None
            self.highlighted_moves = []
            self.actions_taken = 0
            self.update_display()
            self.set_status(f"Redo: Advanced from turn {old_turn} to turn {new_turn}")
            self.awaiting_command = True

    def next_move(self):
        """Continue to the next turn and make selections"""
        self.set_status("Next clicked")
        self.game._game.save_state()
        if not isinstance(self.game._game.current_player(), HumanPlayer):
            self.ai_move()
            self.set_status(f"Next clicked: AI moved")
        
        if isinstance(self.game._game.current_player(), HumanPlayer):
            self.set_status(f"Next clicked: It's Human turn. Awaiting move...")
        self.awaiting_command = True


    def show_winner(self, winner):
        """Display winning and take input to restart or not"""
        messagebox.showinfo("Game Over", f"{winner.capitalize()} has won the game!")
        if messagebox.askyesno("Play Again", "Would you like to play again?"):
            self.reset_game()
        else:
            self.root.quit()

    def reset_game(self):
        """Helper function to reset the game if the users decide to start another round"""
        self.p1 = type(self.p1)(self.p1.color)
        self.p2 = type(self.p2)(self.p2.color)
        self.game._game.__init__(self.p1, self.p2, self.game._game.current, 
                               self.game._game.caretaker is not None, 
                               self.game._game.display_eval)
        self.selected_piece = None
        self.highlighted_moves = []
        self.actions_taken = 0
        self.update_display()
        
        if not isinstance(self.game._game.current_player(), HumanPlayer):
            self.root.after(1000, self.ai_move)


class Main:
    """
    Main function to start playing the game with GUI
    """
    @staticmethod
    def run():
        """
        Main runner
        """
        args = sys.argv[1:]
        defaults = ['human', 'human', 'off', 'off']
        for i, arg in enumerate(args):
            if i < len(defaults):
                defaults[i] = arg.lower()

        p1_type, p2_type = defaults[0], defaults[1]
        use_history = defaults[2] == 'on'
        verbose = defaults[3] == 'on'

        root = tk.Tk()
        gui = BoardGameGUI(
            root,
            p1_type=p1_type,
            p2_type=p2_type,
            use_history=use_history,
            verbose=verbose
        )
        root.mainloop()

if __name__ == '__main__':
    Main.run()