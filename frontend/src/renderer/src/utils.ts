export const closeApp = () => {
  window.electron.ipcRenderer.send('close')
}

export const minimizeApp = () => {
  window.electron.ipcRenderer.send('minimize')
}

export const showSuccess = (toast) => {
  toast.add({ severity: 'success', summary: 'Sukces', life: 1500 });
};

export const showError = (toast) => {
  toast.add({ severity: 'error', summary: 'Wpisz pytanie', life: 1500 });
};