#!/usr/bin/env python3.7
import iterm2
import subprocess


def run_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    return result.stdout.decode('utf-8')


async def main(connection):
    app = await iterm2.async_get_app(connection)

    @iterm2.RPC
    async def clear():
        window = app.current_terminal_window
        if window is not None:
            # Get the active session in this tab
            sessions = app.current_terminal_window.current_tab.sessions

            for session in sessions:
                # Send text to the session as though the user had typed it
                await session.async_send_text('clear\n')

        else:
            print("No current window")

    @iterm2.RPC
    async def start_server():
        window = app.current_terminal_window
        if window is not None:

            # Get the active session in this tab
            sessions = app.current_terminal_window.current_tab.sessions

            for session in sessions:
                # Send text to the session as though the user had typed it
                await session.async_send_text('yarn start:qa\n')

        else:
            print("No current window")

    @iterm2.RPC
    async def stop_server():
        window = app.current_terminal_window
        if window is not None:

            # Get the active session in this tab
            sessions = app.current_terminal_window.current_tab.sessions
            curr_session = app.current_terminal_window.current_tab.current_session

            await curr_session.async_send_text("\x03\n")
            await curr_session.async_send_text("killall node\n")

            for session in sessions:
                # Send text to the session as though the user had typed it
                await session.async_send_text("clear\n")

        else:
            print("No current window")

    @iterm2.RPC
    async def shutdown():
        window = app.current_terminal_window
        if window is not None:

            tabs = app.current_terminal_window.tabs

            for tab in tabs:
                sessions = tab.sessions
                for session in sessions:
                    # Send text to the session as though the user had typed it
                    await session.async_send_text('\x03\n')

            await window.async_close(force=True)

        else:
            print("No current window")

    @iterm2.RPC
    async def git_push(session_id=iterm2.Reference("id")):
        window = app.current_terminal_window
        if window is not None:
            session = app.current_terminal_window.current_tab.current_session
            # get git branch
            present_working_directory = await session.async_get_variable("path")
            git_branch = run_command(
                f"(cd {present_working_directory};git rev-parse --abbrev-ref HEAD)")
            # get commit message from emoji in terminal prompt
            li = await session.async_get_line_info()
            lines = await session.async_get_contents(li.first_visible_line_number, li.mutable_area_height)
            line_list = list(
                map(lambda line: line.string if line.string else None, lines))
            line_list = [i for i in line_list if i]
            commit_message = line_list[-1].split(' ')[0]

            # run commands
            await session.async_send_text('git add -A\n')
            await session.async_send_text(f'git commit -m "{commit_message}"\n')
            await session.async_send_text(f'git push origin {git_branch}\n')

        else:
            print("No current window")

    @iterm2.RPC
    async def git_pull_staging():
        window = app.current_terminal_window
        if window is not None:

            # Get the active session in this tab
            sessions = app.current_terminal_window.current_tab.sessions

            for session in sessions:
                # Send text to the session as though the user had typed it
                await session.async_send_text("git pull origin @staging --ff\n")

        else:
            print("No current window")

    await clear.async_register(connection)
    await start_server.async_register(connection)
    await stop_server.async_register(connection)
    await shutdown.async_register(connection)
    await git_push.async_register(connection)
    await git_pull_staging.async_register(connection)

iterm2.run_forever(main)
