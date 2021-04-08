def print_success(msg):
    from colorama import Fore, Back, Style
    print(Fore.BLACK + Back.GREEN + msg)
    print(Style.RESET_ALL)


def print_error(msg):
    from colorama import Fore, Back, Style
    print(Fore.BLACK + Back.RED + msg)
    print(Style.RESET_ALL)


def aws_cli(*cmd):
    from awscli.clidriver import create_clidriver
    import os
    old_env = dict(os.environ)
    try:
        # Environment
        env = os.environ.copy()
        env['LC_CTYPE'] = u'en_US.UTF'
        os.environ.update(env)

        # Run awscli in the same process
        exit_code = create_clidriver().main(list(cmd))

        # Deal with problems
        if exit_code > 0:
            raise RuntimeError('AWS CLI exited with code {}'.format(exit_code))
    finally:
        os.environ.clear()
        os.environ.update(old_env)
