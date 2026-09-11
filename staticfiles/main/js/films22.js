function changeContent(tabNumber) {
    // —крываем вкладки
    const contents = document.querySelectorAll('.content');
    contents.forEach(content => {
        content.classList.remove('active');
    });

    // скрываем содержимое вкладок
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.classList.remove('active');
    });

    // ѕоказываем выбранное содержимое и добавл€ем активный класс к вкладке
    let targetTabElement = document.getElementById('tab' + tabNumber);
    targetTabElement.classList.add('active');
    let targetContentElement = document.getElementById('content' + tabNumber);
    targetContentElement.classList.add('active');
}

function preventUncheck(checkbox) {
  // ≈сли пытаютс€ сн€ть галку с первого чекбокса, возвращаем ее обратно
  if (checkbox.id === 'checkbox1' && !checkbox.checked) {
    checkbox.checked = true;
  }
}

function toggleReady(checkbox) {
  const allCheckbox = document.getElementById('checkbox1');
  const aucCheckbox = document.getElementById('checkbox2');
  const buyCheckbox = document.getElementById('checkbox3');

  // —нимаем галки с других чекбоксов
  if (checkbox.id === 'checkbox1' && checkbox.checked) {
    aucCheckbox.checked = false;
    buyCheckbox.checked = false;
  } else if (checkbox.id === 'checkbox2' && checkbox.checked) {
    allCheckbox.checked = false;
    buyCheckbox.checked = false;
  } else if (checkbox.id === 'checkbox3' && checkbox.checked) {
    allCheckbox.checked = false;
    aucCheckbox.checked = false;
  }

  // ≈сли снимают галку со второго или третьего чекбокса,
  // автоматически активируем первый чекбокс
  if ((checkbox.id === 'checkbox2' || checkbox.id === 'checkbox3') && !checkbox.checked) {
    allCheckbox.checked = true;
  }

  const rows = document.querySelectorAll('tbody tr');

  // ѕоказываем все строки
  // класс check-ready означает, что строка должна быть активирована (показана) чекбоксом
  if (allCheckbox.checked) {
    rows.forEach(row => {
      if (row.classList.contains('month-active') && row.classList.contains('nickname-active')) {
          row.classList.remove('hidden');
      }
      row.classList.add('check-ready');
    })
  } else if (aucCheckbox.checked) {
    // —крываем строки с классом "buy"
    rows.forEach(row => {
      if (row.classList.contains('buy')) {
        row.classList.add('hidden');
        row.classList.remove('check-ready');
      } else {
        // если строка не содержит отметку активированного фильтром мес€ца или никнейма, то не показываем еЄ
        if (row.classList.contains('month-active') && row.classList.contains('nickname-active')) {
            row.classList.remove('hidden');
        }
        row.classList.add('check-ready');
      }
    });
  } else if (buyCheckbox.checked) {
    // —крываем строки с классом "auc"
    rows.forEach(row => {
      if (row.classList.contains('auc')) {
        row.classList.add('hidden');
        row.classList.remove('check-ready');
      } else {
        // если строка не содержит отметку активированного фильтром мес€ца или никнейма, то не показываем еЄ
        if (row.classList.contains('month-active') && row.classList.contains('nickname-active')) {
            row.classList.remove('hidden');
        }
        row.classList.add('check-ready');
      }
    });
  } else {
    // ≈сли ни один чекбокс не выбран, показываем все строки
    rows.forEach(row => {
      if (row.classList.contains('month-active') && row.classList.contains('nickname-active')) {
          row.classList.remove('hidden');
      }
      row.classList.add('check-ready');
    })
  }
  updateResultsCounter();
}

const MONTHS_RU = { 1: '€нвар€', 2: 'феврал€', 3: 'марта', 4: 'апрел€', 5: 'ма€', 6: 'июн€', 7: 'июл€', 8: 'августа',
                    9: 'сент€бр€', 10: 'окт€бр€', 11: 'но€бр€', 12: 'декабр€' };
const MONTH_RU_2 = {
    '€нвар€': '€нварь',
    'феврал€': 'февраль',
    'марта': 'март',
    'апрел€': 'апрель',
    'ма€': 'май',
    'июн€': 'июнь',
    'июл€': 'июль',
    'августа': 'август',
    'сент€бр€': 'сент€брь',
    'окт€бр€': 'окт€брь',
    'но€бр€': 'но€брь',
    'декабр€': 'декабрь',
}

// ‘ункци€ дл€ фильтрации записей по выбранному мес€цу
function filterByMonth() {
    const selectElement = document.querySelector('#month-select');
    const selectedMonthYear = selectElement.value.toLowerCase();
    const rows = Array.from(document.querySelectorAll('#results-table-body > tr'));

    if (!selectedMonthYear) {
        return;
    }

    // —окрытие строк, которые не относ€тс€ к выбранному мес€цу
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

// ‘ункци€ дл€ фильтрации записей по выбранному никнейму
function filterByNickname() {
    const selectElement = document.querySelector('#nickname-select');
    const selectedNickname = selectElement.value;
    const rows = Array.from(document.querySelectorAll('#results-table-body > tr'));

    if (!selectedNickname) {
        return;
    }

    // —окрытие строк, которые не относ€тс€ к выбранному мес€цу
    rows.forEach(row => {
        if (selectedNickname != 'all') {
            const currentNickname = row.cells[5].innerText;
            if (!currentNickname.includes(selectedNickname)) {
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
    // ѕоказываем все строки по умолчанию
    let counter = 0;
    rows.forEach(row => {
        if (!row.classList.contains('hidden')) { counter++; }
    });
    document.querySelector('.results-counter').querySelector('span').innerText = `${counter}`;
}

// закрытие всех открытых спойлеров при открытии нового
function toggleSpoilers(event) {
    const summaries = document.querySelectorAll('.film-main-container summary');

    summaries.forEach(summary => {
        const details = summary.parentElement;
        // «акрываем все спойлеры, кроме того, на который кликнули
        if (details !== event.currentTarget) {
            details.removeAttribute('open'); // «акрываем спойлер
        }
    });
}

// открытие или закрытие сразу всех спойлеров
function toggleSpoilersAll(option) {
    const summaries = document.querySelectorAll('.film-main-container summary');
    if (option == 'open') {
        summaries.forEach(summary => {
            const details = summary.parentElement;
            details.setAttribute('open', '');
        });
    } else {
        summaries.forEach(summary => {
            const details = summary.parentElement;
            details.removeAttribute('open');
        });
    }
}
