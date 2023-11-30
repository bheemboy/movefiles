"use strict"

class MoveFolders {
    bind_vars_and_events = async () => {
        //bind vars
        this.pathLabels =[];
        this.pathLabels[0] = globalThis.document.getElementById("devPath");
        this.pathLabels[1] = globalThis.document.getElementById("qaPath");
        this.pathLabels[2] = globalThis.document.getElementById("releasedPath");

        this.folderList = [];
        this.folderList[0] = globalThis.document.getElementById("devFolders");
        this.folderList[1] = globalThis.document.getElementById("qaFolders");
        this.folderList[2] = globalThis.document.getElementById("releasedFolders");
        
        this.copyDev2QAButton = globalThis.document.getElementById("copyDev2QAButton");
        this.copyQA2DevButton = globalThis.document.getElementById("copyQA2DevButton");
        this.copyQA2ReleasedButton = globalThis.document.getElementById("copyQA2ReleasedButton");
        this.copyReleased2QAButton = globalThis.document.getElementById("copyReleased2QAButton");

        this.delButtons = [];
        this.delButtons[0] = globalThis.document.getElementById("deleteDevButton");
        this.delButtons[1] = globalThis.document.getElementById("deleteQAButton");
        this.delButtons[2] = globalThis.document.getElementById("deleteReleasedButton");

        this.statusMessage = globalThis.document.getElementById("statusMessage");
        this.progressMessage = globalThis.document.getElementById("progressMessage");

        // bind events
        const _movefolder = this;
        this.copyDev2QAButton.addEventListener("click", async function() {
            _movefolder.copy_selected_item(0, 1);
        });
        this.copyQA2DevButton.addEventListener("click", async function() {
            _movefolder.copy_selected_item(1, 0);
        });
        this.copyQA2ReleasedButton.addEventListener("click", async function() {
            _movefolder.copy_selected_item(1, 2);
        });
        this.copyReleased2QAButton.addEventListener("click", async function() {
            _movefolder.copy_selected_item(2, 1);
        });

        this.delButtons.forEach((delButton, index) => {
            delButton.addEventListener("click", async function() {
                _movefolder.delete_selected_item(index);
            });
        });

        this.socket = io();
        this.socket.on('connect', function() {
            console.log('socket connected');
            // _movefolder.socket.emit('my event', {data: 'I\'m connected!'});
        });

        this.socket.on('state', function(state) {
            _movefolder.display_state(state);
        });
    }

    // get and display root paths
    display_paths = async (paths) => {
        this.pathLabels.forEach((element, index) => {
            element.textContent = paths[index];
        });
    }

    disable_buttons = async (disable) => {
        this.copyDev2QAButton.disabled = disable;
        this.copyQA2DevButton.disabled = disable;
        this.copyQA2ReleasedButton.disabled = disable;
        this.copyReleased2QAButton.disabled = disable;

        this.delButtons.forEach((delButton, index) => {
            delButton.disabled = disable;
        });
    }


    // Populate subfolders select lists
    display_subfolders = async (subfolders) => {
        this.folderList.forEach((element, index) => {
            
            while (element.hasChildNodes()) element.removeChild(element.firstChild);
            
            subfolders[index].forEach(subfolder => {
                const option = globalThis.document.createElement("option");
                option.value = subfolder[0];
                option.textContent = `${subfolder[0]} (${subfolder[1]} MB)`;
                element.appendChild(option);
            });
        });
    }

    display_statusMessage = async (msg) => {
        this.statusMessage.textContent = msg; 
    }

    display_progresslines(progressLines) {
        var ul = globalThis.document.createElement('ul');
        progressLines.forEach(line => {
            var item = globalThis.document.createElement('li');
            item.textContent = line;
            ul.appendChild(item);
        });
        this.progressMessage.innerHTML = ul.innerHTML;
        window.scrollTo(0, globalThis.document.body.scrollHeight);
    }

    display_state = async (state) => {
        this.state = state;
        this.display_paths(state.paths);
        this.disable_buttons(state.disable_btns);
        this.display_subfolders(state.subfolders);
        this.display_statusMessage(state.statusMessage);
        this.display_progresslines(state.progressLines);
    }

    copy_selected_item = async (from, to) => {
        const sub_folder = this.folderList[from].value;
        
        if (sub_folder == "") {
            this.statusMessage.textContent = "Select an item to copy"; 
        }
        else {
            const response = await fetch(`/copy_folder?src_path=${this.state.paths[from]}&sub_folder=${sub_folder}&dest_path=${this.state.paths[to]}`);
            const state = await response.json();
            this.display_state(state);
        }
    }

    delete_selected_item = async (index) => {
        const sub_folder = this.folderList[index].value;
        
        if (sub_folder == "") {
            this.statusMessage.textContent = "Select an item to delete"; 
        }
        else {
            if (confirm(`Press OK to delete ${sub_folder}`) == true) {
                const response = await fetch(`/delete_folder?src_path=${this.state.paths[index]}&sub_folder=${sub_folder}`);
                const state = await response.json();
                this.display_state(state);
            }
        }
    }
};

var app = new MoveFolders();
document.addEventListener("DOMContentLoaded", async function() {
    app.bind_vars_and_events();
});
