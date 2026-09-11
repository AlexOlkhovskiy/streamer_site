function preventUncheck(checkbox) {
  // Если пытаются снять галку с первого чекбокса, возвращаем ее обратно
  if (checkbox.id === 'checkbox1' && !checkbox.checked) {
    checkbox.checked = true;
  }
}

function toggleReady(checkbox) {
  const allCheckbox = document.getElementById('checkbox1');
  const readyCheckbox = document.getElementById('checkbox2');
  const notReadyCheckbox = document.getElementById('checkbox3');

  // Снимаем галки с других чекбоксов
  if (checkbox.id === 'checkbox1' && checkbox.checked) {
    readyCheckbox.checked = false;
    notReadyCheckbox.checked = false;
  } else if (checkbox.id === 'checkbox2' && checkbox.checked) {
    allCheckbox.checked = false;
    notReadyCheckbox.checked = false;
  } else if (checkbox.id === 'checkbox3' && checkbox.checked) {
    allCheckbox.checked = false;
    readyCheckbox.checked = false;
  }

  // Если снимают галку со второго или третьего чекбокса,
  // автоматически активируем первый чекбокс
  if ((checkbox.id === 'checkbox2' || checkbox.id === 'checkbox3') && !checkbox.checked) {
    allCheckbox.checked = true;
  }

  const rows = document.querySelectorAll('tbody tr');

  // Показываем все строки
  // класс check-ready означает, что строка должна быть активирована (показана) чекбоксом
  if (allCheckbox.checked) {
    rows.forEach(row => {
      if (row.classList.contains('month-active') && row.classList.contains('nickname-active')) {
          row.classList.remove('hidden');
      }
      row.classList.add('check-ready');
    })
  } else if (readyCheckbox.checked) {
    // Скрываем строки с классом "not-ready"
    rows.forEach(row => {
      if (row.classList.contains('not-ready')) {
        row.classList.add('hidden');
        row.classList.remove('check-ready');
      } else {
        // если строка не содержит отметку активированного фильтром месяца или никнейма, то не показываем её
        if (row.classList.contains('month-active') && row.classList.contains('nickname-active')) {
            row.classList.remove('hidden');
        }
        row.classList.add('check-ready');
      }
    });
  } else if (notReadyCheckbox.checked) {
    // Скрываем строки с классом "ready"
    rows.forEach(row => {
      if (row.classList.contains('ready')) {
        row.classList.add('hidden');
        row.classList.remove('check-ready');
      } else {
        // если строка не содержит отметку активированного фильтром месяца или никнейма, то не показываем её
        if (row.classList.contains('month-active') && row.classList.contains('nickname-active')) {
            row.classList.remove('hidden');
        }
        row.classList.add('check-ready');
      }
    });
  } else {
    // Если ни один чекбокс не выбран, показываем все строки
    rows.forEach(row => {
      if (row.classList.contains('month-active') && row.classList.contains('nickname-active')) {
          row.classList.remove('hidden');
      }
      row.classList.add('check-ready');
    })
  }
  updateResultsCounter();
}

const MONTHS_RU = { 1: 'СЏРЅРІР°СЂСЏ', 2: 'С„РµРІСЂР°Р»СЏ', 3: 'РјР°СЂС‚Р°', 4: 'Р°РїСЂРµР»СЏ', 5: 'РјР°СЏ', 6: 'РёСЋРЅСЏ', 7: 'РёСЋР»СЏ', 8: 'Р°РІРіСѓСЃС‚Р°',
                    9: 'СЃРµРЅС‚СЏР±СЂСЏ', 10: 'РѕРєС‚СЏР±СЂСЏ', 11: 'РЅРѕСЏР±СЂСЏ', 12: 'РґРµРєР°Р±СЂСЏ' };
const MONTH_RU_2 = {
    'СЏРЅРІР°СЂСЏ': 'СЏРЅРІР°СЂСЊ',
    'С„РµРІСЂР°Р»СЏ': 'С„РµРІСЂР°Р»СЊ',
    'РјР°СЂС‚Р°': 'РјР°СЂС‚',
    'Р°РїСЂРµР»СЏ': 'Р°РїСЂРµР»СЊ',
    'РјР°СЏ': 'РјР°Р№',
    'РёСЋРЅСЏ': 'РёСЋРЅСЊ',
    'РёСЋР»СЏ': 'РёСЋР»СЊ',
    'Р°РІРіСѓСЃС‚Р°': 'Р°РІРіСѓСЃС‚',
    'СЃРµРЅС‚СЏР±СЂСЏ': 'СЃРµРЅС‚СЏР±СЂСЊ',
    'РѕРєС‚СЏР±СЂСЏ': 'РѕРєС‚СЏР±СЂСЊ',
    'РЅРѕСЏР±СЂСЏ': 'РЅРѕСЏР±СЂСЊ',
    'РґРµРєР°Р±СЂСЏ': 'РґРµРєР°Р±СЂСЊ',
}

// Функция для фильтрации записей по выбранному месяцу
function filterByMonth() {
    const selectElement = document.querySelector('#month-select');
    const selectedMonthYear = selectElement.value.toLowerCase();
    const rows = Array.from(document.querySelectorAll('#results-table-body > tr'));

    if (!selectedMonthYear) {
        return;
    }

    // Сокрытие строк, которые не относятся к выбранному месяцу
    rows.forEach(row => {
        if (selectedMonthYear != 'all') {
            const month = row.cells[0].innerText.split(' ')[1];
            const year = row.cells[0].innerText.split(' ')[2];
            const currentDatetimeText = `${MONTH_RU_2[month]} ${year}`;

            if (currentDatetimeText !== selectedMonthYear) {
                row.classList.add('hidden');
                row.classList.remove('month-active');
            } else {
                if (row.classList.contains('nickname-active') && row.classList.contains('check-ready')) {
                    row.classList.remove('hidden');
                }
                row.classList.add('month-active');
            }
        } else {
            row.classList.add('month-active');
            if (row.classList.contains('nickname-active') && row.classList.contains('check-ready')) {
                row.classList.remove('hidden');
            } else {
                row.classList.add('hidden');
            }
        }
    });
    updateResultsCounter();
}

// Функция для фильтрации записей по выбранному никнейму
function filterByNickname() {
    const selectElement = document.querySelector('#nickname-select');
    const selectedNickname = selectElement.value;
    const rows = Array.from(document.querySelectorAll('#results-table-body > tr'));

    if (!selectedNickname) {
        return;
    }

    // Сокрытие строк, которые не относятся к выбранному месяцу
    rows.forEach(row => {
        if (selectedNickname != 'all') {
            const currentNickname = row.cells[1].innerText;
            if (currentNickname !== selectedNickname) {
                row.classList.add('hidden');
                row.classList.remove('nickname-active');
            } else {
                if (row.classList.contains('month-active') && row.classList.contains('check-ready')) {
                    row.classList.remove('hidden');
                }
                row.classList.add('nickname-active');
            }
        } else {
            row.classList.add('nickname-active');
            if (row.classList.contains('month-active') && row.classList.contains('check-ready')) {
                row.classList.remove('hidden');
            } else {
                row.classList.add('hidden');
            }
        }
    });
    updateResultsCounter();
}

function updateResultsCounter() {
    const rows = Array.from(document.querySelectorAll('#results-table-body > tr'));
    // Показываем все строки по умолчанию
    let counter = 0;
    rows.forEach(row => {
        if (!row.classList.contains('hidden')) { counter++; }
    });
    document.querySelector('.results-counter').querySelector('span').innerText = `Р’СЃРµРіРѕ Р·Р°РїРёСЃРµР№: ${counter}`;
}

// закрытие всех открытых спойлеров при открытии нового
function toggleSpoilers(event) {
    const summaries = document.querySelectorAll('.faq-container summary');

    summaries.forEach(summary => {
        const details = summary.parentElement;
        // Закрываем все спойлеры, кроме того, на который кликнули
        if (details !== event.currentTarget) {
            details.removeAttribute('open'); // Закрываем спойлер
        }
    });
}
