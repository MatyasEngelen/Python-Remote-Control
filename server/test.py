from screeninfo import get_monitors
for m in get_monitors():
    if m.is_primary:
        print(str(m.width) + " " + str(m.height))

print(get_monitors())