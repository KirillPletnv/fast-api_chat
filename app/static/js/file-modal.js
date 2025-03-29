document.addEventListener('DOMContentLoaded', function() {
                    // Элементы модального окна
                    const fileModal = document.getElementById('fileModal');
                    const openFileModalBtn = document.getElementById('openFileModal');
                    const closeFileModal = fileModal.querySelector('.close');

                    // Элементы формы
                    const uploadForm = document.getElementById('uploadFileForm');
                    const fileInput = document.getElementById('fileInput');
                    const fileNameInput = document.getElementById('fileName');
                    const filesList = document.getElementById('filesList');

                    // Управление модальным окном
                    openFileModalBtn.addEventListener('click', () => {
                        fileModal.style.display = 'block';
                        loadFiles(); // Загружаем список файлов при открытии
                    });

                    closeFileModal.addEventListener('click', () => {
                        fileModal.style.display = 'none';
                    });

                    window.addEventListener('click', (event) => {
                        if (event.target === fileModal) {
                            fileModal.style.display = 'none';
                        }
                    });

                    // Обработка отправки формы
                    uploadForm.addEventListener('submit', async (e) => {
                        e.preventDefault();

                        const formData = new FormData();
                        formData.append('file_name', fileNameInput.value);
                        formData.append('file', fileInput.files[0]);




                        try {
                            const response = await fetch('/api_v1/chat/upload-file/', {
                                method: 'POST',
                                body: formData
                            });

                            if (!response.ok) {
                                throw new Error('Ошибка загрузки файла');
                            }

                            const result = await response.json();
                            alert(`Файл "${result.filename}" успешно загружен!`);
                            uploadForm.reset();
                            loadFiles(); // Обновляем список файлов
                        } catch (error) {
                            console.error('Ошибка:', error);
                            alert('Ошибка при загрузке файла: ' + error.message);
                        }
                    });

                    // Загрузка списка файлов
                    async function loadFiles() {
                        try {
                            const response = await fetch('/api_v1/chat/list-files/');
                            if (!response.ok) {
                                throw new Error('Ошибка получения списка файлов');
                            }

                            const data = await response.json();
                            filesList.innerHTML = '';

                            if (data.files && data.files.length > 0) {
                                data.files.forEach(file => {
                                    const fileItem = document.createElement('div');
                                    fileItem.className = 'file-item';

                                    const link = document.createElement('a');
                                    link.href = `/api_v1/chat/download-file/${file.name}`;
                                    link.textContent = `${file.name} (${formatSize(file.size)})`;
                                    link.download = file.name;

                                    fileItem.appendChild(link);
                                    filesList.appendChild(fileItem);
                                });
                            } else {
                                filesList.innerHTML = '<p>Нет загруженных файлов</p>';
                            }
                        } catch (error) {
                            console.error('Ошибка:', error);
                            filesList.innerHTML = '<p>Ошибка загрузки списка файлов</p>';
                        }
                    }

                    // Форматирование размера файла
                    function formatSize(bytes) {
                        if (bytes < 1024) return bytes + ' байт';
                        if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
                        return (bytes / 1048576).toFixed(1) + ' MB';
                    }
                });
