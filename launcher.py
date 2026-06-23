import os
from app.main import main

if __name__ == '__main__':
    if os.name == 'nt':
        os.system('title 企鹅弹幕机')
    main()
