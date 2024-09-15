# epserver installer
# Done by: MrAlphaQ

echo "\e[1;30;42mDone by: MrAlphaQ\e[0m"
echo "\e[30;42mInstalling epserver...\e[0m"
chmod +x ./epserver.py
echo "\e[30;41msudo is required to copy the file to /usr/bin\e[0m"
sudo cp ./epserver.py /usr/bin/epserver
mkdir -p ~/epserver && mkdir -p ~/epserver/uploads ~/epserver/linux ~/epserver/windows
cp ./favicon.ico ~/epserver && cp -r ./templates ./windows ./linux ~/epserver
echo "\e[30;42mepserver has been installed successfully!\e[0m"
echo "\e[1;32mIF YOU WANT TO ADD YOUR OWN TOOLS, ADD THEM TO THE ~/epserver LINUX OR WINDOWS FOLDERS\e[0m"
echo "\e[1;32mTo run the program, type 'epserver' in the terminal\e[0m"