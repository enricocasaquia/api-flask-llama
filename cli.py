import click
import json
import sys
import ollama
from app import app
from sql_alchemy import db
from models.user import UserModel
from models.history import ChatHistoryModel

with open("./conf/config.json") as config_json:
    config = json.load(config_json)

MODEL_NAME = config.get('OLLAMA_MODEL', 'llama3.1:8b-instruct-q4_K_M')
CONTEXT_SIZE = config.get('CONTEXT_WINDOW_SIZE', 10)

db.init_app(app)

@click.group()
def cli():
    """
    Command-line interface (CLI) tool for the Flask Llama API project.
    """
    pass

@cli.command()
@click.option('--login', prompt='Login for the new user', help='User login')
@click.option('--password', prompt='Password', hide_input=True, confirmation_prompt=True, help='User password')
def create_user(login, password):
    with app.app_context():
        db.create_all()
        if UserModel.find_user_login(login):
            click.secho(f"Error: The user '{login}' already exists.", fg='red')
            return
        try:
            user = UserModel(login=login, password=password, active=True)
            user.insert_user()
            click.secho(f"Success! User '{login}' created with the ID {user.id}.", fg='green')
        except Exception as e:
            click.secho(f"Error while creating user.", fg='red')

@cli.command()
def list_users():
    with app.app_context():
        users = UserModel.query.all()
        if not users:
            click.echo("No users found in the database!")
            return
        
        click.echo(f"\n{'ID':<5} | {'Login':<20} | {'Active':<10}")
        click.echo("-" * 40)
        for user in users:
            status = "Sim" if user.active else "Não"
            click.echo(f"{user.id:<5} | {user.login:<20} | {status:<10}")
        click.echo("")

@cli.command()
@click.argument('login')
def delete_user(login):
    with app.app_context():
        user = UserModel.find_user_login(login)
        if not user:
            click.secho(f"User '{login}' not found.", fg='red')
            return
            
        if click.confirm(f"Are you sure you want to DELETE the user '{login}'?"):
            try:
                user.delete_user()
                click.secho(f"User '{login}' deleted.", fg='green')
            except Exception as e:
                click.secho(f"Error while deleting user.", fg='red')

@cli.command()
@click.option('--login', prompt='Login', help='Your login to load chat history')
@click.option('--password', prompt='Password', hide_input=True, help='Your password')
def chat(login, password):
    with app.app_context():
        user = UserModel.find_user_login(login)
        if not user or not UserModel.check_password(password, user.password):
            click.secho("Invalid credentials.", fg='red')
            sys.exit(1)
        
        user_id = user.id
        click.clear()
        click.secho(f"=== Chat CLI (Model: {MODEL_NAME}) ===", fg='blue', bold=True)
        click.echo(f"Logged user: {user.login}")
        click.echo("Commands: /exit to close, /delete to delete chat history.\n")

    client = ollama.Client()

    while True:
        try:
            text_input = click.prompt(click.style("You", fg='green'))
        except (KeyboardInterrupt, EOFError):
            break

        if text_input.strip().lower() in ['/exit', 'exit', 'quit']:
            click.echo("See you next time!")
            break
            
        with app.app_context():
            if text_input.strip().lower() in ['/delete', 'clear']:
                ChatHistoryModel.delete_history_by_user(user_id)
                click.secho("Chat history deleted!", fg='yellow')
                continue

            history_objs = ChatHistoryModel.find_history_user(user_id, CONTEXT_SIZE)
            messages = [{'role': h.role, 'content': h.content} for h in history_objs]
            
        messages.append({'role': 'user', 'content': text_input})

        click.echo(click.style("Ollama: ", fg='cyan'), nl=False)
        try:
            stream = client.chat(model=MODEL_NAME, messages=messages, stream=True)
            
            full_response = ""
            for chunk in stream:
                content = chunk['message']['content']
                print(content, end='', flush=True)
                full_response += content
            print("\n")

            with app.app_context():
                ChatHistoryModel(user_id, 'user', text_input).insert_history()
                ChatHistoryModel(user_id, 'assistant', full_response).insert_history()

        except Exception as e:
            click.secho(f"\nError communicating with Ollama.", fg='red')

if __name__ == '__main__':
    cli()