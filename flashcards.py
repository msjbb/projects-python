import argparse
import io
import itertools
import json

log_file = io.StringIO()


def f_print(msg):
    """ Print to console and string buffer. """
    print(msg)
    log_file.seek(0, io.SEEK_END)
    log_file.write(msg + '\n')


def f_input():
    """ Collect user input and save to string buffer. """
    user_in = input()
    log_file.seek(0, io.SEEK_END)
    log_file.write('> ' + user_in + '\n')

    return user_in


def add_flashcard(cards: dict):
    """ Add a new flashcard to the deck. """
    f_print('The card')
    term = f_input()

    while term in cards.keys():
        f_print(f'The term "{term}" already exists. Try again:')
        term = f_input()

    f_print('The definition of the card')
    definition = f_input()

    while definition in [x['definition'] for x in cards.values()]:
        f_print(f'The definition "{definition}" already exists. Try again:')
        definition = f_input()

    cards[term] = {'definition': definition,
                   'mistakes': 0}
    log_file.seek(0, io.SEEK_END)
    f_print(f'The pair ("{term}":"{definition}") has been added.')
    return cards


def remove_flashcard(cards: dict):
    """ Remove a term from the flashcard deck. """
    f_print('Which card?')
    term = f_input()
    try:
        cards.pop(term)
        f_print('The card has been removed.')
    except KeyError:
        f_print(f'Can\'t remove "{term}": there is no such card.')
    return cards


def import_flashcards(existing_cards: dict, filename: str = None):
    """ Import existing flashcards from a file of the user's choice. """
    if filename:
        f_print(f'File name:\n> {filename}')
    else:
        f_print('File name:\n')
        filename = f_input()

    new_cards = {}
    try:
        with open(filename, 'r') as file:
            new_cards = json.load(file)
        f_print(f'{len(new_cards)} cards have been loaded.')
    except FileNotFoundError:
        f_print('File not found.')

    new_dict = existing_cards.copy()
    new_dict.update(new_cards)
    return new_dict


def export_flashcards(cards: dict, filename: str = None):
    if filename is None:
        f_print('File name:')
        filename = f_input()

    with open(f'{filename}', 'w') as f:
        f.write(json.dumps(cards))

    f_print(f'{len(cards)} cards have been saved.')


def ask_definitions(cards):
    card_terms = list(cards.keys())
    card_defs = [x['definition'] for x in cards.values()]

    # ASK
    f_print('How many times to ask?')
    num_cards = int(f_input())

    buffer = itertools.cycle(cards.items())
    i = 1
    for term, details in buffer:
        if i > num_cards:
            break

        f_print(f'Print the definition of "{term}":')
        answer = f_input()

        if details['definition'] == answer:
            f_print('Correct!')
        elif answer in card_defs:
            alt_term = card_terms[card_defs.index(answer)]
            f_print(f'Wrong...The right answer is "{details["definition"]}", '
                    + f'but your definition is correct for "{alt_term}"')
            cards[term]['mistakes'] += 1
        else:
            f_print(f'Wrong...The right answer is "{details["definition"]}".')
            cards[term]['mistakes'] += 1

        i += 1

    return cards


def hardest_card(cards):
    """ Determine the last maximum number of mistakes and logger.info all terms
    with that mistake count.
    """
    max_errors = 0
    term_list = []
    # cycle through list to update max error value
    # find which members also have that value
    for term, details in cards.items():
        if details['mistakes'] > max_errors:
            max_errors = details['mistakes']
            term_list.clear()
            term_list.append(term)
        elif details['mistakes'] == max_errors & max_errors > 0:
            term_list.append(term)
        else:
            continue

    if max_errors == 0:
        f_print('There are no cards with errors.')
    else:
        if len(term_list) > 1:
            terms = ', '.join([f'"{x}"' for x in term_list])
            f_print(f'The hardest cards are {terms}. You have {max_errors} errors answering them.')
        else:
            f_print(f'The hardest card is "{term_list[0]}". You have {max_errors} errors answering it.')


def save_log():
    """ Write all console input/output to a file of a given name. """
    f_print('File name:')
    file_name = f_input()
    with open(file_name, 'w') as f:
        f.write(log_file.getvalue())

    f_print('The log has been saved.')


def reset_stats(cards):
    """ Set the mistake count for all cards to zero. """
    for term in cards.keys():
        cards[term]['mistakes'] = 0
    f_print('Card statistics have been reset.')
    return cards


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='This program test terms of imported or newly created flashcards and tracks success statistics.')
    parser.add_argument('-i', '--import_from', help='The name of the file containing the flashcards to import.')
    parser.add_argument('-e', '--export_to', help='The filename to export flashcards to upon exiting the program')
    args = parser.parse_args()

    flashcards = {}

    if args.import_from:
        flashcards = import_flashcards(flashcards, args.import_from)

    while True:
        f_print('Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):')
        action = f_input()

        if action == 'add':
            flashcards = add_flashcard(flashcards)
        if action == 'remove':
            flashcards = remove_flashcard(flashcards)
        if action == 'import':
            flashcards = import_flashcards(flashcards)
        if action == 'export':
            export_flashcards(flashcards)
        if action == 'ask':
            flashcards = ask_definitions(flashcards)
        if action == 'exit':
            if args.export_to:
                export_flashcards(flashcards, args.export_to)

            print('Bye bye!')
            break
        if action == 'log':
            save_log()
        if action == 'hardest card':
            hardest_card(flashcards)
        if action == 'reset stats':
            flashcards = reset_stats(flashcards)
