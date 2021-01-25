#!/usr/bin/python3
import curses
import time
from curses import wrapper
import random

def main (stdscr):
    stdscr.clear()

    curses.init_pair (1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair (2, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair (3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    
    # Initialize sample string
    # The 10 text files are indexed 00-09
    indexes_used = [None] * 10
    i = 0
    while i < 10:
        n = random.randint(0, 9)
        if n not in indexes_used:
            indexes_used[i] = n
            i += 1
    
    string = ""
    for i in indexes_used:
        with open("./text/%02d.txt" % i, "r") as f:
            string += f.read()
    offset = 0
    bufsize = (curses.LINES - 2) * curses.COLS
    
    newline_comp = 0
    j = k = 0 # buffer index and string index
    buf = ""
    while j < bufsize:
        buf += string[k + offset]
        if string[k + offset] != '\n':
            j += 1
        else:
            j += curses.COLS - ((k + newline_comp) % curses.COLS)
            newline_comp += curses.COLS - ((k + newline_comp) % curses.COLS) - 1
        k += 1

    stdscr.addstr(1, 0, buf)
    stdscr.refresh()
    
    # Variables for tabulation
    # List of characters where an error was made
    error_list = []
    error_count = 0
    chars_typed = 0
    cancelled = False

    stdscr.addstr(0, 0, "%-35s 5:00" % "Start typing to start the timer.")
    stdscr.chgat(0, 0, -1, curses.A_REVERSE)
    stdscr.move(1, 0)
    stdscr.refresh()
    c = stdscr.getch()
    timer_start = time.time() 
    stdscr.addstr(0, 0, "%-35s" % "Typing test in progress...", curses.A_REVERSE)
    stdscr.addstr(0, 41, "%-23s" % "Press ^X to cancel test", curses.A_REVERSE)

    stdscr.nodelay(True)
    curses.ungetch(c)
   
    i = 0
    while i < len(string):
        # Refresh time
        time_remaining = 300 - time.time() + timer_start
        if time_remaining <= 0:
            break
        yx = curses.getsyx()
        stdscr.addstr(0, 35, "%2d:%02d" % (time_remaining // 60, time_remaining % 60), curses.A_REVERSE)
        stdscr.move(yx[0], yx[1])
        stdscr.refresh()

        # Interpret input
        c = stdscr.getch()
        # No input ready
        if c == curses.ERR:
            continue
        # Input ready
        else:
            # Character is ASCII printable or newline
            if (31 < c and c < 127) or (c == curses.KEY_ENTER or c == 10 or c == 13):
                if i in error_list:
                    error_list.remove(i)
                # Character is correct
                if chr(c) == string[i]:
                    stdscr.addstr(chr(c), curses.color_pair(1))
                # Not correct
                else:
                    curses.beep()
                    if c == curses.KEY_ENTER or c == 10 or c == 13:
                        # Reassign as space character
                        c = 32
                    stdscr.addstr(chr(c), curses.color_pair(2))
                    error_list.append(i)
                    error_count += 1
                i += 1
                chars_typed += 1
                
                stdscr.refresh()

            # Other conditions
            elif c == curses.KEY_BACKSPACE or c == curses.KEY_LEFT:
                if i > 0:
                    i -= 1

                yx = curses.getsyx()
                # Cursor is at first column
                if yx[1] == 0:
                    if yx[0] > 1:
                        y = yx[0] - 1
                        x = curses.COLS - 1
                    else:
                        curses.beep()
                        y = 1
                        x = 0
                    stdscr.move(y, x)
                    stdscr.addstr(string[i])
                    stdscr.move(y, x) 
                # Cursor is elsewhere
                else:
                    stdscr.addstr('\b' + string[i] + '\b')
                stdscr.refresh()
            elif c == ord('X') & 0x1f:
                cancelled = True
                break

    # Loop has exited
    time_elapsed = time.time() - timer_start
    # if due to timeout
    if not cancelled:
        stdscr.addstr(0, 0, "%-35s 0:00" % "Typing test finished!", curses.A_REVERSE)
    # if cancelled by user
    else:
        stdscr.addstr(0, 0, "%-35s" % "Typing test ended!")
        stdscr.chgat(0, 0, -1, curses.color_pair(2) | curses.A_BOLD)
    stdscr.chgat(0, 35, 5, curses.color_pair(2) | curses.A_BOLD | curses.A_BLINK)
    
    # Display statistics
    uncorrected = len(error_list)
    stdscr.addstr(1, 0, "%-34s" % " ", curses.color_pair(3))
    stdscr.addstr(2, 0, "%-34s" % "        TYPING STATISTICS", curses.color_pair(3))
    stdscr.addstr(3, 0, "  Gross characters typed:%7d  " % chars_typed, curses.color_pair(3))
    stdscr.addstr(4, 0, "  Net characters typed:  %7d  " % i, curses.color_pair(3))
    stdscr.addstr(5, 0, "  Total errors made:     %7d  " % error_count, curses.color_pair(3))
    stdscr.addstr(6, 0, "  Uncorrected errors:    %7d  " % uncorrected, curses.color_pair(3))
    stdscr.addstr(7, 0, "  Time elapsed:         %2d:%05.2f  " % (time_elapsed // 60, time_elapsed % 60), curses.color_pair(3))
    stdscr.addstr(8, 0, "%-34s" % " ", curses.color_pair(3))
    stdscr.addstr(9, 0, "  Gross typing speed:   %4d WPM  " % (12 * chars_typed / time_elapsed), curses.color_pair(3))
    stdscr.addstr(10, 0, "  Net typing speed:     %4d WPM  " % (60 * ((chars_typed / 5) - uncorrected) / time_elapsed), curses.color_pair(3))
    if chars_typed == 0:
        # Trick calculations into displaying 0
        chars_typed = error_count = 1
    stdscr.addstr(11, 0, "  Accuracy:                %4d%%  " % round(100 * (chars_typed - error_count) / chars_typed), curses.color_pair(3))
    stdscr.addstr(12, 0, "%-34s" % " ", curses.color_pair(3))
    stdscr.addstr(13, 0, "%-34s" % "  Press Ctrl+X to exit...", curses.color_pair(3))
    stdscr.addstr(14, 0, "%-34s" % " ", curses.color_pair(3))
    curses.curs_set(False)
    stdscr.refresh()


    stdscr.nodelay(False)
    while stdscr.getch() != ord('X') & 0x1f:
        pass
    # done

wrapper (main)
