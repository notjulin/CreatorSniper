/*
 * Constants
*/

const base_url = `${location.protocol}//${location.hostname}:${location.port}`

const input_link_regex = /^https:\/\/socialclub\.rockstargames\.com\/job\/gtav\/([\w-]{22})$/gm

/*
 * Variables
*/

let last_content_id = ''
let last_content_lang = ''
let last_content_data = {}

let loading_content = false

/*
 * Essentials
*/

const url_for = (path) => `${base_url}/${path}`
const id_for = (id) => document.getElementById(id)

/*
 * HTML elements
*/

const overlay_name = id_for('overlay-name')
const overlay_description = id_for('overlay-description')
const overlay_image = id_for('overlay-image')
const overlay_tags = id_for('overlay-tags')

const input_link = id_for('input-link')
const input_name = id_for('input-name')
const input_tags = id_for('input-tags')
const input_editor = id_for('input-editor')

const textarea_description = id_for('textarea-description')
const textarea_editor = id_for('textarea-editor')

const img_image = id_for('img-image')

const button_send = id_for('button-send')
const button_cancel = id_for('button-cancel')
const button_clone = id_for('button-clone')
const button_editor = id_for('button-editor')
const button_update = id_for('button-update')
const button_reload = id_for('button-reload')

const div_editor = id_for('div-editor')
const div_content = id_for('div-content')

const select_presets = id_for('select-presets')

const modal_notification = id_for('modal-notification')

const p_notification = id_for('p-notification')

const list_clone = id_for('list-clone')
const list_management = id_for('list-management')

const modal = new bootstrap.Modal(modal_notification)

/*
 * Helper functions
*/

const show = (element) => element.removeAttribute('hidden')
const hide = (element) => element.setAttribute('hidden', '')

const enable = (element) => element.removeAttribute('disabled')
const disable = (element) => element.setAttribute('disabled', '')

const show_overlays = (element) => [].forEach.call(element.getElementsByClassName('placeholder'), (element) => show(element))
const hide_overlays = (element) => [].forEach.call(element.getElementsByClassName('placeholder'), (element) => hide(element))

const trigger_input = (element, text) => {
    element.value = text
    element.dispatchEvent(new KeyboardEvent('keyup', { code: 'backspace' }))
}

const resolve_path = (object, path) => path
    .split(/[\.\[\]\'\"]/)
    .filter(p => p)
    .reduce((o, p) => o[p], object)

const set_path = (object, path, value) => path
    .split('.')
    .reduce((o, p, i) => o[p] = path.split('.').length === ++i ? value : o[p] || {}, object)

const show_notification = (text_value) => {
    p_notification.innerHTML = text_value
    modal.show()
}

const load_image = (file, element) => {
    if (!file.name.endsWith('.jpg') &&
        !file.name.endsWith('.jpeg') &&
        !file.name.endsWith('.png') &&
        !file.name.endsWith('.gif')) {
        show_notification('Error: Invalid image extension.')
        return
    }

    const reader = new FileReader()

    reader.onload = (event) => element.src = event.target.result
    reader.readAsDataURL(file)
}

const content_for = (content) => `https://socialclub.rockstargames.com/job/gtav/${content}`

const toggle_spin = (element) => {
    const loader = '<i class="bx bx-loader-alt bx-spin me-sm-1"></i>'

    if (!element.getElementsByTagName('i').length) {
        element.innerHTML = '<i class="bx bx-loader-alt bx-spin me-sm-1"></i>' + element.innerHTML
    } else {
        element.innerHTML = element.innerHTML.replace(loader, '')
    }
}

const clone_content = (content) => {
    list_clone.click()
    trigger_input(input_link, content_for(content))
    button_send.click()
}

const delete_content = (content) => {
    (async () => {
        const response = await fetch(
            url_for('delete'),
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id: content
                })
            }
        );

        if (response.status !== 200) {
            show_notification(`Error: HTTP ${response.status}`)
            return
        }

        show_notification('Success: Content has been deleted.')

        id_for(`-content-${content}`).remove()
    })();
}

/*
 * Event listeners
*/

window.ondragover = (event) => {
    event.stopPropagation()
    event.preventDefault()
}

window.ondrop = (event) => {
    event.stopPropagation()
    event.preventDefault()
}

window.onload = () => {
    hide(input_name)
    hide(input_tags)

    hide(textarea_description)

    hide(img_image)

    disable(button_send)
    disable(button_cancel)
    disable(button_clone)

    disable(select_presets)
    disable(input_editor)
    disable(button_editor)

    hide(textarea_editor)
}

input_link.onkeyup = () => {
    disable(button_send)

    while ((m = input_link_regex.exec(input_link.value)) !== null) {
        if (m.index === input_link_regex.lastIndex) {
            input_link_regex.lastIndex++
        }

        m.forEach((match, index) => {
            if (index === 1) {
                last_content_id = match

                enable(button_send)
            }
        })
    }
}

button_send.onclick = () => {
    (async () => {
        const response = await fetch(url_for('data'), {
            method: 'POST',
            headers: {
                'content-type': 'application/json'
            },
            body: JSON.stringify({ id: last_content_id })
        })

        if (response.status !== 200) {
            show_notification(`Error: HTTP ${response.status}`)
            return
        }

        const content = await response.json()

        if (content.error) {
            show_notification(`Error: Exception ${content.error}`)
            return
        }

        input_name.value = content.name
        input_tags.value = content.tags.join(',')

        textarea_description.value = content.desc

        img_image.src = content.image

        last_content_lang = content.lang
        last_content_data = content.data

        show(input_name)
        show(input_tags)

        show(textarea_description)

        show(img_image)

        enable(button_cancel)
        enable(button_clone)

        hide_overlays(overlay_name)
        hide_overlays(overlay_tags)
        hide_overlays(overlay_description)
        hide_overlays(overlay_image)

        disable(input_link)
        disable(button_send)

        trigger_input(input_editor, '')

        enable(select_presets)
        enable(input_editor)

        show(textarea_editor)
    })()
}

button_cancel.onclick = () => {
    input_link.value = ''
    input_name.value = ''
    input_tags.value = ''

    textarea_description.value = ''

    img_image.src = ''

    hide(input_name)
    hide(input_tags)

    hide(textarea_description)

    hide(img_image)

    disable(button_cancel)
    disable(button_clone)

    show_overlays(overlay_name)
    show_overlays(overlay_tags)
    show_overlays(overlay_description)
    show_overlays(overlay_image)

    enable(input_link)

    select_presets.options.selectedIndex = 0

    input_editor.value = ''

    textarea_editor.value = ''

    disable(select_presets)
    disable(input_editor)
    disable(button_editor)

    hide(textarea_editor)

    last_content_id = ''
    last_content_lang = ''
    last_content_data = {}
}

overlay_image.ondrop = (event) => {
    if (img_image.hasAttribute('hidden')) {
        return
    }

    if (event.dataTransfer.files.length) {
        load_image(event.dataTransfer.files[0], img_image)
    }
}

overlay_image.onclick = () => {
    if (img_image.hasAttribute('hidden')) {
        return
    }

    new Promise((resolve) => {
        const input_tmp = document.createElement('input')

        input_tmp.type = 'file'
        input_tmp.onchange = () => {
            if (input_tmp.files.length) {
                resolve(input_tmp.files[0])
            }
        }
        input_tmp.click()
    }).then((file) => load_image(file, img_image))
}

input_editor.onkeyup = () => {
    disable(button_editor)

    let value = input_editor.value

    o = last_content_data
    value = value.replace(/\[(\w+)\]/, '.$1').replace(/^\./, '')

    let a = value.split('.')

    for (let i = 0, n = a.length; i < n; ++i) {
        textarea_editor.value = ''

        let k = a[i]

        if (i === a.length - 1) {
            let ik = 0
            let mk = 0
            let ol = Object.keys(o).length

            for (let key in o) {
                if (key.startsWith(a[n - 1])) {
                    let ok = o[key]

                    if (ik === ol - 1) {
                        textarea_editor.value += `${key} (${typeof ok}) ${ok}`
                    } else {
                        textarea_editor.value += `${key} (${typeof ok}) ${ok}\n`
                    }

                    mk++
                }

                ik++
            }

            if (mk > 10) {
                textarea_editor.setAttribute('rows', '10')
            } else {
                textarea_editor.setAttribute('rows', mk)
            }

            textarea_editor.scrollTo(0, 0)
        }

        if (typeof o === 'object' && k in o) {
            o = o[k]
        } else {
            return
        }
    }

    enable(button_editor)
}

button_editor.onclick = () => {
    div_editor.innerHTML = ''

    const value = input_editor.value

    if (!value.length || value.endsWith('.')) {
        show_notification('Error: Invalid or malformed input.')
        return
    }

    const path = resolve_path(last_content_data, value)

    if (path === undefined) {
        show_notification('Error: Could not find the path.')
        return
    }

    if (typeof path === 'object') {
        const size = Object.keys(path).length

        if (size > 20) {
            show_notification('Error: Too many elements.')
            return
        }

        let index = 0

        for (const key in path) {
            const path_value = path[key]

            if (typeof path_value !== 'object') {
                div_editor.innerHTML += `
                <div id="-modal-${index}" ${index === size - 1 ? '' : 'class="mb-1"'}>
                    <label class="form-label fs-sm">${key} <small class="text-muted">(${typeof path_value})</small></label>
                    <input class="form-control form-control-sm bg-secondary border-0" type="text" autocomplete="off" value="${path_value}">
                    <input class="form-control" type="hidden" value="${value}.${key}">
                </div>`
            }

            index++
        }
    } else {
        const path_key = value.split('.').pop()

        div_editor.innerHTML = `
        <div id="-modal-0">
            <label class="form-label fs-sm">${path_key} <small class="text-muted">(${typeof path})</small></label>
            <input class="form-control form-control-sm bg-secondary border-0" type="text" autocomplete="off" value="${path}">
            <input class="form-control" type="hidden" value="${value}">
        </div>`
    }
}

button_update.onclick = () => {
    const nodes = div_editor.childNodes
    let index = 0

    nodes.forEach((node) => {
        if (node.nodeType === 1) {
            const element = id_for(`-modal-${index}`)
            const elements = element.getElementsByClassName('form-control')
            const value_type = element.getElementsByTagName('small')[0].innerText
            const value = elements[0].value
            const path = elements[1].value

            if (value_type === '(string)') {
                set_path(last_content_data, path, value)
            } else if (value_type === '(number)') {
                if (!isNaN(value)) {
                    if (value.includes('.')) {
                        set_path(last_content_data, path, parseFloat(value))
                    } else {
                        set_path(last_content_data, path, parseInt(value))
                    }
                } else {
                    set_path(last_content_data, path, 0)
                }
            } else if (value_type === '(boolean)') {
                set_path(last_content_data, path, value === 'true')
            } else {
                set_path(last_content_data, path, null)
            }

            index++
        }
    })

    div_editor.innerHTML = ''

    trigger_input(input_editor, input_editor.value)
}

button_clone.onclick = () => {
    (async () => {
        toggle_spin(button_clone)
        disable(button_clone)

        const response = await fetch(
            url_for('clone'),
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id: last_content_id,
                    name: input_name.value,
                    desc: textarea_description.value,
                    tags: input_tags.value,
                    image: img_image.src,
                    data: last_content_data,
                    lang: last_content_lang
                })
            }
        );

        if (response.status !== 200) {
            toggle_spin(button_clone)
            enable(button_clone)

            show_notification(`Error: HTTP ${response.status}`)
            return
        }

        const content = await response.json()

        if (content.error) {
            toggle_spin(button_clone)
            enable(button_clone)

            show_notification(`Error: Exception ${content.error}`)
            return
        }

        toggle_spin(button_clone)
        enable(button_clone)

        show_notification(
            `Success: The content has been cloned.
            <br>
            <small class="text-muted">
                (<a class="text-decoration-none" target="_blank" href="${content_for(content.id)}">${content.id}</a> -> <a class="text-decoration-none" target="_blank" href="${content_for(content.new_id)}">${content.new_id}</a>)
            </small>`
        )
    })();
}

button_reload.onclick = () => {
    loading_content = false
    list_management.click()
}

list_management.onclick = () => {
    (async () => {
        if (loading_content) {
            return
        }

        loading_content = true

        toggle_spin(button_reload)
        disable(button_reload)

        show_notification('Warning: This might take a few seconds.')

        const response = await fetch(url_for('list'));

        if (response.status !== 200) {
            toggle_spin(button_reload)
            enable(button_reload)

            show_notification(`Error: HTTP ${response.status}`)
            return
        }

        div_content.innerHTML = ''

        const content = await response.json()

        if (content.error) {
            toggle_spin(button_reload)
            enable(button_reload)

            show_notification(`Error: Exception ${content.error}`)
            return
        }

        const contents = content.contents

        contents.forEach((content) => {
            div_content.innerHTML += `
            <div id="-content-${content.id}" class="card border-0 shadow-sm overflow-hidden mb-4">
                <div class="row g-0">
                    <img class="col-sm-4 bg-repeat-0 bg-position-center bg-size-cover"
                        src="data:image/jpeg;base64,${content.image}" style="max-width: 300px">
                    <div class="col-sm-8">
                        <div class="card-body">
                            <h2 class="h5 pb-1 mb-2">${content.name}</h2>
                            <p class="mb-3">
                                ID: <a class="text-decoration-none" target="_blank" href="${content_for(content.id)}">${content.id}</a>
                            </p>
                            <div class="d-flex">
                                <button onclick="clone_content('${content.id}')" type="button"
                                    class="btn btn-outline-primary px-3 px-lg-4 me-3">
                                    <i class="bx bx-edit fs-xl me-xl-2"></i>
                                    <span class="d-none d-xl-inline">Clone</span>
                                </button>
                                <button onclick="delete_content('${content.id}')" type="button"
                                    class="btn btn-outline-danger px-3 px-lg-4">
                                    <i class="bx bx-trash-alt fs-xl me-xl-2"></i>
                                    <span class="d-none d-xl-inline">Delete</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`
        })

        toggle_spin(button_reload)
        enable(button_reload)
    })();
}