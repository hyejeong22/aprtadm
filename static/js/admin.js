if (document.getElementById('residentTableBody')) {
  loadTableResidents()
}

function loadTableResidents() {
  fetch('/residents')
    .then((res) => res.json())
    .then((data) => {
      allResidents = data.data //
      displayResidents(allResidents)
    })

  const tbody = document.getElementById('residentTableBody')
  tbody.innerHTML = '' // 기존 내용 지우기

  data.forEach((resident) => {
    const row = document.createElement('tr')
    row.innerHTML = `
  <td>${resident.name}</td>
  <td>${resident.address}</td>
  <td>${resident.phone}</td>
  <td>
    <button onclick="editResident(${resident.id})">수정</button>
    <button onclick="deleteResident(${resident.id})">삭제</button>
  </td>
`

    tbody.appendChild(row)
  })
}

function promptAdminPassword(callback) {
  const password = prompt('관리자 비밀번호를 입력하세요:')
  if (!password) return

  fetch('/verify_password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  })
    .then((res) => {
      if (!res.ok) throw new Error('인증 실패')
      return res.json()
    })
    .then((data) => {
      if (data.status === 'success') {
        callback() // 여기서 editResident 내부 코드가 실행됨
      } else {
        alert('❌ 비밀번호가 틀렸습니다')
      }
    })
    .catch(() => alert('❌ 인증 실패'))
}

document.getElementById('editForm').style.display = 'block'
function editResident(id) {
  promptAdminPassword(() => {
    const resident = allResidents.find((r) => r.id === id)
    if (!resident) return alert('해당 세대주 정보를 찾을 수 없습니다.')

    document.getElementById('editId').value = resident.id
    document.getElementById('editName').value = resident.name
    document.getElementById('editAddress').value = resident.address
    document.getElementById('editPhone').value = resident.phone

    document.getElementById('editForm').style.display = 'block'
    window.scrollTo(0, document.getElementById('editForm').offsetTop)
  })
}

function deleteResident(id) {
  promptAdminPassword((password) => {
    if (!confirm('정말 삭제하시겠습니까?')) return

    fetch(`/residents/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ password: password }), // 👈 여기가 핵심
    })
      .then((res) => {
        if (res.ok) {
          alert('✅ 삭제 완료')
          loadResidents() // 목록 갱신
        } else if (res.status === 401) {
          alert('❌ 비밀번호가 틀렸습니다')
        } else {
          alert('❌ 삭제 실패')
        }
      })
      .catch(() => alert('❌ 서버 오류'))
  })
}
