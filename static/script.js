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
    }

    // get and display root paths
    get_and_display_paths = async () => {
        const get_paths_response = await fetch("/get_paths");
        this.paths = await get_paths_response.json();

        this.pathLabels.forEach((element, index) => {
            element.textContent = this.paths[index];
        });
    }

    // Populate subfolders select lists
    get_and_display_subfolders = async () => {
        const get_subfolders_response = await fetch("/get_subfolders");
        const subfolders = await get_subfolders_response.json();

        this.folderList.forEach((element, index) => {
            
            while (element.hasChildNodes()) element.removeChild(element.firstChild);
            
            subfolders[index].forEach(subfolder => {
                const option = globalThis.document.createElement("option");
                option.value = subfolder;
                option.textContent = subfolder;
                element.appendChild(option);
            });
        });
    }

    copy_selected_item = async (from, to) => {
        const sub_folder = this.folderList[from].value;
        
        if (sub_folder == "") {
            this.statusMessage.textContent = "Select an item to copy"; 
        }
        else {
            const copy_folder_response = await fetch(`/copy_folder?src_path=${this.paths[from]}&sub_folder=${sub_folder}&dest_path=${this.paths[to]}`);
            const msg = await copy_folder_response.json();

            this.statusMessage.textContent = msg.message;
            this.get_and_display_subfolders();
        }
    }

    delete_selected_item = async (index) => {
        const sub_folder = this.folderList[index].value;
        
        if (sub_folder == "") {
            this.statusMessage.textContent = "Select an item to delete"; 
        }
        else {
            if (confirm(`Press OK to delete ${sub_folder}`) == true) {
                const delete_folder_response = await fetch(`/delete_folder?src_path=${this.paths[index]}&sub_folder=${sub_folder}`);
                const msg = await delete_folder_response.json();

                this.statusMessage.textContent = msg.message;
                this.get_and_display_subfolders();
            }
        }
    }
};

var app = new MoveFolders();
document.addEventListener("DOMContentLoaded", async function() {
    app.bind_vars_and_events();
    app.get_and_display_paths();
    app.get_and_display_subfolders();
});


