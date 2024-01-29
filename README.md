## Design of Flask Application for Fantasy Football App

### HTML Files

1. `index.html`:
   - Serves as the homepage of the application.
   - Contains elements like login/signup forms, links to join/create leagues, and general information about the app.

2. `leagues.html`:
   - Displays the list of all leagues the user is a part of and provides options to join or create a new league.

3. `league_dashboard.html`:
   - The dashboard for an individual league.
   - Displays team stats, standings, and upcoming fixtures.
   - Provides options to make player transactions, change lineup, and view league chat.

4. `player_list.html`:
   - Displays a comprehensive list of players available for selection, including stats, rankings, and ownership percentages.

5. `draft_room.html`:
   - Real-time draft room where users can participate in live drafts, make picks, and view draft results.

6. `chat.html`:
   - A dedicated chat page for each league, allowing users to communicate with fellow league members.

### Routes

1. `/login`:
   - Handles user login and authentication.
   - Redirects to the user's league dashboard on successful login.

2. `/signup`:
   - Handles user registration and account creation.
   - Sends a confirmation email to the user and redirects to the login page.

3. `/leagues`:
   - Displays the list of all leagues the user is a part of.
   - Provides options to join or create a new league.

4. `/create_league`:
   - Handles the process of league creation.
   - Collects league details, invites members, and sets up the initial draft order.

5. `/join_league`:
   - Handles the process of joining a league.
   - Prompts the user to enter the league access code and adds them to the league.

6. `/league_dashboard`:
   - Displays the dashboard for an individual league.
   - Provides access to team stats, standings, fixtures, players, and chat.

7. `/make_transaction`:
   - Handles player transactions, such as adding/dropping players, making trades, and setting the lineup.

8. `/draft_room`:
   - Initializes the real-time draft room for a specific league.
   - Provides a live view of the draft, allowing users to make picks and view draft results.

9. `/chat`:
   - Initializes the chat page for a specific league.
   - Allows users to send and receive messages, view chat history, and participate in discussions.