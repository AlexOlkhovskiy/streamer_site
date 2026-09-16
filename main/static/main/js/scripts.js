function preventUncheck(checkbox) {
  // ���� �������� ����� ����� � ������� ��������, ���������� �� �������
  if (checkbox.id === 'checkbox1' && !checkbox.checked) {
    checkbox.checked = true;
  }
}

function toggleReady(checkbox) {
  const allCheckbox = document.getElementById('checkbox1');
  const readyCheckbox = document.getElementById('checkbox2');
  const notReadyCheckbox = document.getElementById('checkbox3');

  // ������� ����� � ������ ���������
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

  // ���� ������� ����� �� ������� ��� �������� ��������,
  // ������������� ���������� ������ �������
  if ((checkbox.id === 'checkbox2' || checkbox.id === 'checkbox3') && !checkbox.checked) {
    allCheckbox.checked = true;
  }

  const rows = document.querySelectorAll('tbody tr');

  // ���������� ��� ������
  // ����� check-ready ��������, ��� ������ ������ ���� ������������ (��������) ���������
  if (allCheckbox.checked) {
    rows.forEach(row => {
      if (row.classList.contains('month-active') && row.classList.contains('nickname-active') && row.classList.contains('result-active')) {
          row.classList.remove('hidden');
      }
      row.classList.add('check-ready');
    })
  } else if (readyCheckbox.checked) {
    // �������� ������ � ������� "not-ready"
    rows.forEach(row => {
      if (row.classList.contains('not-ready')) {
        row.classList.add('hidden');
        row.classList.remove('check-ready');
      } else {
        // ���� ������ �� �������� ������� ��������������� �������� ������, �������� ��� �������, �� �� ���������� �
        if (row.classList.contains('month-active') && row.classList.contains('nickname-active') && row.classList.contains('result-active')) {
            row.classList.remove('hidden');
        }
        row.classList.add('check-ready');
      }
    });
  } else if (notReadyCheckbox.checked) {
    // �������� ������ � ������� "ready"
    rows.forEach(row => {
      if (row.classList.contains('ready')) {
        row.classList.add('hidden');
        row.classList.remove('check-ready');
      } else {
        // ���� ������ �� �������� ������� ��������������� �������� ������, �������� ��� �������, �� �� ���������� �
        if (row.classList.contains('month-active') && row.classList.contains('nickname-active') && row.classList.contains('result-active')) {
            row.classList.remove('hidden');
        }
        row.classList.add('check-ready');
      }
    });
  } else {
    // ���� �� ���� ������� �� ������, ���������� ��� ������
    rows.forEach(row => {
      if (row.classList.contains('month-active') && row.classList.contains('nickname-active') && row.classList.contains('result-active')) {
          row.classList.remove('hidden');
      }
      row.classList.add('check-ready');
    })
  }
  updateResultsCounter();
}


const MONTH_RU_2 = {
    'января': 'январь',
    'февраля': 'февраль',
    'марта': 'март',
    'апреля': 'апрель',
    'мая': 'май',
    'июня': 'июнь',
    'июля': 'июль',
    'августа': 'август',
    'сентября': 'сентябрь',
    'октября': 'октябрь',
    'ноября': 'ноябрь',
    'декабря': 'декабрь',
}

// ������� ��� ���������� ������� �� ���������� ������
function filterByMonth() {
    const selectElement = document.querySelector('#month-select');
    const selectedMonthYear = selectElement.value.toLowerCase();
    const rows = Array.from(document.querySelectorAll('#results-table-body > tr'));

    if (!selectedMonthYear) {
        return;
    }

    // �������� �����, ������� �� ��������� � ���������� ������
    rows.forEach(row => {
        if (selectedMonthYear != 'all') {
            const month = row.cells[0].innerText.split(' ')[1];
            const year = row.cells[0].innerText.split(' ')[2];
            const currentDatetimeText = `${MONTH_RU_2[month]} ${year}`;

            if (currentDatetimeText !== selectedMonthYear) {
                row.classList.add('hidden');
                row.classList.remove('month-active');
            } else {
                if (row.classList.contains('nickname-active') && row.classList.contains('result-active') && row.classList.contains('check-ready')) {
                    row.classList.remove('hidden');
                }
                row.classList.add('month-active');
            }
        } else {
            row.classList.add('month-active');
            if (row.classList.contains('nickname-active') && row.classList.contains('result-active') && row.classList.contains('check-ready')) {
                row.classList.remove('hidden');
            } else {
                row.classList.add('hidden');
            }
        }
    });
    updateResultsCounter();
}

// ������� ��� ���������� ������� �� ���������� ��������
function filterByNickname() {
    const selectElement = document.querySelector('#nickname-select');
    const selectedNickname = selectElement.value;
    const rows = Array.from(document.querySelectorAll('#results-table-body > tr'));

    if (!selectedNickname) {
        return;
    }

    rows.forEach(row => {
        if (selectedNickname != 'all') {
            const currentNickname = row.cells[1].innerText;
            if (currentNickname !== selectedNickname) {
                row.classList.add('hidden');
                row.classList.remove('nickname-active');
            } else {
                if (row.classList.contains('month-active') && row.classList.contains('result-active') && row.classList.contains('check-ready')) {
                    row.classList.remove('hidden');
                }
                row.classList.add('nickname-active');
            }
        } else {
            row.classList.add('nickname-active');
            if (row.classList.contains('month-active') && row.classList.contains('result-active') && row.classList.contains('check-ready')) {
                row.classList.remove('hidden');
            } else {
                row.classList.add('hidden');
            }
        }
    });
    updateResultsCounter();
}

// ������� ��� ���������� ������� �� ��������� ������� � �������
function filterByResult() {
    const selectElement = document.querySelector('#result-select');
    const selectedResult = selectElement.value;
    const rows = Array.from(document.querySelectorAll('#results-table-body > tr'));

    if (!selectedResult) {
        return;
    }

    rows.forEach(row => {
        if (selectedResult != 'all') {
            const currentResult = row.cells[3].innerText;
            if (currentResult !== selectedResult) {
                row.classList.add('hidden');
                row.classList.remove('result-active');
            } else {
                if (row.classList.contains('month-active') && row.classList.contains('nickname-active') && row.classList.contains('check-ready')) {
                    row.classList.remove('hidden');
                }
                row.classList.add('result-active');
            }
        } else {
            row.classList.add('result-active');
            if (row.classList.contains('month-active') && row.classList.contains('nickname-active') && row.classList.contains('check-ready')) {
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
    // ���������� ��� ������ �� ���������
    let counter = 0;
    rows.forEach(row => {
        if (!row.classList.contains('hidden')) { counter++; }
    });
    document.querySelector('.results-counter').querySelector('span').innerText = `Всего записей: ${counter}`;
}


