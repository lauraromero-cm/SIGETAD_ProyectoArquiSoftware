import React, { useEffect, useMemo, useState } from 'react'
import { Briefcase, Users, ClipboardList, History, Star, LogOut, UserRound, ShieldCheck } from 'lucide-react'
import { api, authApi, clearSession, getUser, setSession } from './api.js'

const ESTADOS = ['postulado', 'en_revision', 'entrevista', 'evaluacion', 'finalista', 'rechazado', 'contratado']

function App() {
  const [user, setUser] = useState(getUser())

  if (!user) {
    return <AuthScreen onLogin={setUser} />
  }

  return <Dashboard user={user} onLogout={() => { clearSession(); setUser(null) }} />
}

function AuthScreen({ onLogin }) {
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ correo: 'admin@firmafast.cl', contrasena: 'admin123', nombre: '', telefono: '', profesion: '', experiencia_anios: 0 })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const result = mode === 'login'
        ? await authApi.login(form.correo, form.contrasena)
        : await authApi.register({ ...form, nombre_completo: form.nombre, email: form.correo })
      setSession(result.token, result.user)
      onLogin(result.user)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="brand">
          <ShieldCheck size={34} />
          <div>
            <h1>SIGETAD</h1>
            <p>Sistema de Gestión de Talento y Reclutamiento Digital</p>
          </div>
        </div>

        <div className="tabs">
          <button className={mode === 'login' ? 'active' : ''} onClick={() => setMode('login')}>Ingresar</button>
          <button className={mode === 'register' ? 'active' : ''} onClick={() => setMode('register')}>Registro candidato</button>
        </div>

        <form onSubmit={submit} className="form">
          {mode === 'register' && (
            <>
              <label>Nombre completo<input value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} required /></label>
              <label>Teléfono<input value={form.telefono} onChange={e => setForm({ ...form, telefono: e.target.value })} /></label>
              <label>Profesión<input value={form.profesion} onChange={e => setForm({ ...form, profesion: e.target.value })} /></label>
              <label>Años de experiencia<input type="number" value={form.experiencia_anios} onChange={e => setForm({ ...form, experiencia_anios: Number(e.target.value) })} /></label>
            </>
          )}
          <label>Correo<input type="email" value={form.correo} onChange={e => setForm({ ...form, correo: e.target.value })} required /></label>
          <label>Contraseña<input type="password" value={form.contrasena} onChange={e => setForm({ ...form, contrasena: e.target.value })} required /></label>
          {error && <div className="error">{error}</div>}
          <button className="primary" disabled={loading}>{loading ? 'Procesando...' : mode === 'login' ? 'Entrar' : 'Crear cuenta'}</button>
        </form>

        <div className="hint">
          <strong>Usuarios demo:</strong><br />
          admin@firmafast.cl / admin123<br />
          analista@firmafast.cl / admin123<br />
          jefe@firmafast.cl / admin123<br />
          candidato@correo.cl / admin123
        </div>
      </div>
    </div>
  )
}

function Dashboard({ user, onLogout }) {
  const [section, setSection] = useState(defaultSection(user.rol))

  const menu = useMemo(() => {
    const items = []
    if (user.rol === 'candidato') {
      items.push(['portal', 'Portal Candidato', UserRound])
      items.push(['misPostulaciones', 'Mis postulaciones', ClipboardList])
    }
    if (['admin', 'analista'].includes(user.rol)) {
      items.push(['reclutamiento', 'Panel Reclutamiento', Briefcase])
      items.push(['postulaciones', 'Postulaciones', ClipboardList])
      items.push(['candidatos', 'Candidatos', Users])
    }
    if (['admin', 'jefe_area', 'analista'].includes(user.rol)) {
      items.push(['evaluacion', 'Panel Evaluación', Star])
    }
    if (user.rol === 'admin') {
      items.push(['admin', 'Administración', ShieldCheck])
    }
    items.push(['historial', 'Historial', History])
    return items
  }, [user.rol])

  return (
    <div className="layout">
      <aside className="sidebar">
        <h2>SIGETAD</h2>
        <p className="role">{user.nombre}<br /><span>{labelRol(user.rol)}</span></p>
        <nav>
          {menu.map(([key, label, Icon]) => (
            <button key={key} className={section === key ? 'active' : ''} onClick={() => setSection(key)}><Icon size={18} /> {label}</button>
          ))}
        </nav>
        <button className="logout" onClick={onLogout}><LogOut size={18} /> Salir</button>
      </aside>
      <main className="main">
        {section === 'portal' && <PortalCandidato />}
        {section === 'misPostulaciones' && <Postulaciones mine />}
        {section === 'reclutamiento' && <PanelReclutamiento />}
        {section === 'postulaciones' && <Postulaciones />}
        {section === 'candidatos' && <Candidatos />}
        {section === 'evaluacion' && <Evaluaciones />}
        {section === 'admin' && <Administracion />}
        {section === 'historial' && <Historial />}
      </main>
    </div>
  )
}

function defaultSection(rol) {
  if (rol === 'candidato') return 'portal'
  if (rol === 'jefe_area') return 'evaluacion'
  if (rol === 'admin') return 'admin'
  return 'reclutamiento'
}

function labelRol(rol) {
  return ({ admin: 'Administrador', analista: 'Analista de Selección', jefe_area: 'Jefe de Área', candidato: 'Candidato' })[rol] || rol
}

function PanelReclutamiento() {
  const [vacantes, setVacantes] = useState([])
  const [error, setError] = useState('')
  const [form, setForm] = useState({ titulo: '', descripcion: '', departamento: '', salario_minimo: 0, salario_maximo: 0, requisitos: '' })

  async function load() {
    setVacantes(await api('/vacantes/?solo_abiertas=false'))
  }
  useEffect(() => { load().catch(e => setError(e.message)) }, [])

  async function submit(e) {
    e.preventDefault()
    try {
      await api('/vacantes/', { method: 'POST', body: JSON.stringify(form) })
      setForm({ titulo: '', descripcion: '', departamento: '', salario_minimo: 0, salario_maximo: 0, requisitos: '' })
      await load()
    } catch (e) { setError(e.message) }
  }

  async function cerrar(id) {
    await api(`/vacantes/${id}/cerrar/`, { method: 'POST', body: '{}' })
    await load()
  }

  return <section>
    <Header title="Panel Reclutamiento" subtitle="Crear, listar y cerrar vacantes." />
    {error && <div className="error">{error}</div>}
    <form className="card form grid" onSubmit={submit}>
      <label>Título<input value={form.titulo} onChange={e => setForm({ ...form, titulo: e.target.value })} required /></label>
      <label>Departamento<input value={form.departamento} onChange={e => setForm({ ...form, departamento: e.target.value })} required /></label>
      <label>Salario mínimo<input type="number" value={form.salario_minimo} onChange={e => setForm({ ...form, salario_minimo: Number(e.target.value) })} /></label>
      <label>Salario máximo<input type="number" value={form.salario_maximo} onChange={e => setForm({ ...form, salario_maximo: Number(e.target.value) })} /></label>
      <label className="full">Descripción<textarea value={form.descripcion} onChange={e => setForm({ ...form, descripcion: e.target.value })} required /></label>
      <label className="full">Requisitos<textarea value={form.requisitos} onChange={e => setForm({ ...form, requisitos: e.target.value })} /></label>
      <button className="primary">Crear vacante</button>
    </form>
    <VacantesTable vacantes={vacantes} onCerrar={cerrar} />
  </section>
}

function PortalCandidato() {
  const [vacantes, setVacantes] = useState([])
  const [perfil, setPerfil] = useState(null)
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')

  async function load() {
    setVacantes(await api('/vacantes/'))
    setPerfil(await api('/candidatos/me/'))
  }
  useEffect(() => { load().catch(e => setError(e.message)) }, [])

  async function savePerfil(e) {
    e.preventDefault()
    try {
      setPerfil(await api('/candidatos/me/', { method: 'POST', body: JSON.stringify(perfil) }))
      setMsg('Perfil guardado correctamente')
    } catch (e) { setError(e.message) }
  }

  async function postular(id) {
    try {
      await api('/postulaciones/', { method: 'POST', body: JSON.stringify({ id_vacante: id }) })
      setMsg('Postulación registrada')
    } catch (e) { setError(e.message) }
  }

  return <section>
    <Header title="Portal Candidato" subtitle="Gestiona tu perfil y postula a vacantes abiertas." />
    {error && <div className="error">{error}</div>}
    {msg && <div className="success">{msg}</div>}
    {perfil && <form className="card form grid" onSubmit={savePerfil}>
      <label>Nombre completo<input value={perfil.nombre_completo || ''} onChange={e => setPerfil({ ...perfil, nombre_completo: e.target.value })} /></label>
      <label>Email<input value={perfil.email || ''} onChange={e => setPerfil({ ...perfil, email: e.target.value })} /></label>
      <label>Teléfono<input value={perfil.telefono || ''} onChange={e => setPerfil({ ...perfil, telefono: e.target.value })} /></label>
      <label>Profesión<input value={perfil.profesion || ''} onChange={e => setPerfil({ ...perfil, profesion: e.target.value })} /></label>
      <label>Años experiencia<input type="number" value={perfil.experiencia_anios || 0} onChange={e => setPerfil({ ...perfil, experiencia_anios: Number(e.target.value) })} /></label>
      <label>CV / URL<input value={perfil.cv || ''} onChange={e => setPerfil({ ...perfil, cv: e.target.value })} /></label>
      <label>Foto perfil / URL<input value={perfil.foto_perfil || ''} onChange={e => setPerfil({ ...perfil, foto_perfil: e.target.value })} /></label>
      <button className="primary">Guardar perfil</button>
    </form>}
    <h3>Vacantes disponibles</h3>
    <div className="cards">{vacantes.map(v => <div className="card" key={v.id_vacante}><h3>{v.titulo}</h3><p>{v.descripcion}</p><small>{v.departamento} · ${Number(v.salario_minimo).toLocaleString()} - ${Number(v.salario_maximo).toLocaleString()}</small><button onClick={() => postular(v.id_vacante)}>Postular</button></div>)}</div>
  </section>
}

function VacantesTable({ vacantes, onCerrar }) {
  return <div className="card"><table><thead><tr><th>ID</th><th>Título</th><th>Departamento</th><th>Estado</th><th>Acción</th></tr></thead><tbody>{vacantes.map(v => <tr key={v.id_vacante}><td>{v.id_vacante}</td><td>{v.titulo}</td><td>{v.departamento}</td><td><Badge>{v.estado}</Badge></td><td>{v.estado === 'abierta' && <button onClick={() => onCerrar(v.id_vacante)}>Cerrar</button>}</td></tr>)}</tbody></table></div>
}

function Postulaciones() {
  const user = getUser()
  const [items, setItems] = useState([])
  const [error, setError] = useState('')

  async function load() { setItems(await api('/postulaciones/')) }
  useEffect(() => { load().catch(e => setError(e.message)) }, [])

  async function change(id, estado) {
    await api(`/postulaciones/${id}/estado/`, { method: 'POST', body: JSON.stringify({ estado }) })
    await load()
  }

  return <section><Header title="Postulaciones" subtitle="Seguimiento del estado de candidatos." />{error && <div className="error">{error}</div>}<div className="card"><table><thead><tr><th>ID</th><th>Candidato</th><th>Vacante</th><th>Estado</th><th>Fecha</th>{user?.rol !== 'candidato' && <th>Cambiar estado</th>}</tr></thead><tbody>{items.map(p => <tr key={p.id_postulacion}><td>{p.id_postulacion}</td><td>{p.candidato_nombre}</td><td>{p.vacante_titulo}</td><td><Badge>{p.estado}</Badge></td><td>{p.fecha_postulacion?.slice(0,10)}</td>{user?.rol !== 'candidato' && <td><select value={p.estado} onChange={e => change(p.id_postulacion, e.target.value)}>{ESTADOS.map(s => <option key={s} value={s}>{s}</option>)}</select></td>}</tr>)}</tbody></table></div></section>
}

function Candidatos() {
  const [items, setItems] = useState([])
  const [q, setQ] = useState('')
  const [error, setError] = useState('')

  async function load() { setItems(await api(`/candidatos/?q=${encodeURIComponent(q)}`)) }
  useEffect(() => { load().catch(e => setError(e.message)) }, [])

  return <section><Header title="Candidatos" subtitle="Consulta de postulantes registrados." />{error && <div className="error">{error}</div>}<div className="toolbar"><input placeholder="Buscar por nombre, email o profesión" value={q} onChange={e => setQ(e.target.value)} /><button onClick={load}>Buscar</button></div><div className="card"><table><thead><tr><th>ID</th><th>Nombre</th><th>Email</th><th>Profesión</th><th>Experiencia</th><th>CV</th></tr></thead><tbody>{items.map(c => <tr key={c.id_candidato}><td>{c.id_candidato}</td><td>{c.nombre_completo}</td><td>{c.email}</td><td>{c.profesion}</td><td>{c.experiencia_anios} años</td><td>{c.cv}</td></tr>)}</tbody></table></div></section>
}

function Evaluaciones() {
  const [postulaciones, setPostulaciones] = useState([])
  const [form, setForm] = useState({ id_postulacion: '', calificacion: 5, comentarios: '' })
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')

  useEffect(() => { api('/postulaciones/').then(setPostulaciones).catch(e => setError(e.message)) }, [])

  async function submit(e) {
    e.preventDefault()
    try {
      await api('/evaluaciones/', { method: 'POST', body: JSON.stringify(form) })
      setMsg('Evaluación registrada')
      setForm({ id_postulacion: '', calificacion: 5, comentarios: '' })
    } catch (e) { setError(e.message) }
  }

  return <section><Header title="Panel Evaluación" subtitle="Registrar calificación y comentarios." />{error && <div className="error">{error}</div>}{msg && <div className="success">{msg}</div>}<form className="card form" onSubmit={submit}><label>Postulación<select value={form.id_postulacion} onChange={e => setForm({ ...form, id_postulacion: e.target.value })} required><option value="">Seleccionar</option>{postulaciones.map(p => <option key={p.id_postulacion} value={p.id_postulacion}>#{p.id_postulacion} - {p.candidato_nombre} / {p.vacante_titulo}</option>)}</select></label><label>Calificación<select value={form.calificacion} onChange={e => setForm({ ...form, calificacion: Number(e.target.value) })}>{[1,2,3,4,5].map(n => <option key={n} value={n}>{n}</option>)}</select></label><label>Comentarios<textarea value={form.comentarios} onChange={e => setForm({ ...form, comentarios: e.target.value })} /></label><button className="primary">Registrar evaluación</button></form></section>
}

function Administracion() {
  const [usuarios, setUsuarios] = useState([])
  const [form, setForm] = useState({ nombre: '', correo: '', rol: 'analista', contrasena: 'admin123' })
  const [error, setError] = useState('')

  async function load() { setUsuarios(await api('/usuarios/')) }
  useEffect(() => { load().catch(e => setError(e.message)) }, [])
  async function submit(e) { e.preventDefault(); try { await api('/usuarios/', { method: 'POST', body: JSON.stringify(form) }); setForm({ nombre: '', correo: '', rol: 'analista', contrasena: 'admin123' }); await load() } catch (e) { setError(e.message) } }

  return <section><Header title="Panel Administración" subtitle="Gestión simple de usuarios y roles." />{error && <div className="error">{error}</div>}<form className="card form grid" onSubmit={submit}><label>Nombre<input value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} required /></label><label>Correo<input type="email" value={form.correo} onChange={e => setForm({ ...form, correo: e.target.value })} required /></label><label>Rol<select value={form.rol} onChange={e => setForm({ ...form, rol: e.target.value })}><option value="admin">admin</option><option value="analista">analista</option><option value="jefe_area">jefe_area</option><option value="candidato">candidato</option></select></label><label>Contraseña<input value={form.contrasena} onChange={e => setForm({ ...form, contrasena: e.target.value })} /></label><button className="primary">Crear usuario</button></form><div className="card"><table><thead><tr><th>ID</th><th>Nombre</th><th>Correo</th><th>Rol</th><th>Estado</th></tr></thead><tbody>{usuarios.map(u => <tr key={u.id_usuario}><td>{u.id_usuario}</td><td>{u.nombre}</td><td>{u.correo}</td><td>{u.rol}</td><td><Badge>{u.estado}</Badge></td></tr>)}</tbody></table></div></section>
}

function Historial() {
  const [id, setId] = useState('')
  const [items, setItems] = useState([])
  const [error, setError] = useState('')
  async function load() { setItems(await api(`/historial/${id ? `?id_postulacion=${id}` : ''}`)) }
  useEffect(() => { load().catch(e => setError(e.message)) }, [])
  return <section><Header title="Historial" subtitle="Trazabilidad de eventos del proceso." />{error && <div className="error">{error}</div>}<div className="toolbar"><input placeholder="ID postulación opcional" value={id} onChange={e => setId(e.target.value)} /><button onClick={load}>Consultar</button></div><div className="card"><table><thead><tr><th>Fecha</th><th>Postulación</th><th>Tipo</th><th>Descripción</th><th>Usuario</th></tr></thead><tbody>{items.map(h => <tr key={h.id_historial}><td>{h.fecha?.slice(0,16).replace('T',' ')}</td><td>{h.id_postulacion}</td><td><Badge>{h.tipo}</Badge></td><td>{h.descripcion}</td><td>{h.usuario_nombre}</td></tr>)}</tbody></table></div></section>
}

function Header({ title, subtitle }) { return <div className="header"><h1>{title}</h1><p>{subtitle}</p></div> }
function Badge({ children }) { return <span className="badge">{children}</span> }

export default App
