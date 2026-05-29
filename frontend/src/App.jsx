import React, { useEffect, useMemo, useState } from 'react'
import { Briefcase, Users, ClipboardList, History, Star, LogOut, UserRound, ShieldCheck, X } from 'lucide-react'
import { api, authApi, clearSession, getUser, setSession } from './api.js'

const firmaLogo = new URL('./firmafast-logo.png', import.meta.url).href

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
  const [form, setForm] = useState({ correo: 'admin@firmafast.cl', contrasena: 'admin123', nombre: '', telefono: '', profesion: '', experiencia_anios: '' })
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
          <img src={firmaLogo} alt="FirmaFast" />
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
              <label>Años de experiencia<select value={form.experiencia_anios} onChange={e => setForm({ ...form, experiencia_anios: e.target.value })}>
                <option value="">Seleccionar...</option>
                <option value="0">0 años</option>
                <option value="1">1 año</option>
                <option value="2">2 años</option>
                <option value="3">3 años</option>
                <option value="4">4 años</option>
                <option value="5+">5 o más años</option>
              </select></label>
            </>
          )}
          <label>Correo<input type="email" value={form.correo} onChange={e => setForm({ ...form, correo: e.target.value })} required /></label>
          <label>Contraseña<input type="password" value={form.contrasena} onChange={e => setForm({ ...form, contrasena: e.target.value })} required /></label>
          {error && <div className="error">{error}</div>}
          <button className="primary" disabled={loading}>{loading ? 'Procesando...' : mode === 'login' ? 'Entrar' : 'Crear cuenta'}</button>
        </form>
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
      <label>Salario mínimo<input type="text" placeholder="Ej: 1500000" value={form.salario_minimo ? Number(form.salario_minimo).toLocaleString('es-CL') : ''} onChange={e => setForm({ ...form, salario_minimo: parseInt(e.target.value.replace(/\./g, '')) || 0 })} /></label>
      <label>Salario máximo<input type="text" placeholder="Ej: 2500000" value={form.salario_maximo ? Number(form.salario_maximo).toLocaleString('es-CL') : ''} onChange={e => setForm({ ...form, salario_maximo: parseInt(e.target.value.replace(/\./g, '')) || 0 })} /></label>
      <label className="full">Descripción<textarea value={form.descripcion} onChange={e => setForm({ ...form, descripcion: e.target.value })} required /></label>
      <label className="full">Requisitos<textarea value={form.requisitos} onChange={e => setForm({ ...form, requisitos: e.target.value })} /></label>
      <button className="primary">Crear vacante</button>
    </form>
    <VacantesTable vacantes={vacantes} onCerrar={cerrar} />
  </section>
}

function PortalCandidato() {
  const [vacantes, setVacantes] = useState([])
  const [postulaciones, setPostulaciones] = useState([])
  const [perfil, setPerfil] = useState(null)
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')

  async function load() {
    setVacantes(await api('/vacantes/'))
    setPerfil(await api('/candidatos/me/'))
    setPostulaciones(await api('/postulaciones/'))
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
      setMsg('¡Felicidades! Tu postulación fue registrada correctamente.')
      setTimeout(() => setMsg(''), 4000)
      load()
    } catch (e) { setError(e.message) }
  }

  const vacantePostulada = (id) => postulaciones.some(p => p.id_vacante === id)

  return <section>
    <Header title="Portal Candidato" subtitle="Gestiona tu perfil y postula a vacantes abiertas." />
    {error && <div className="error">{error}</div>}
    {msg && <div className="success">{msg}</div>}
    {perfil && <form className="card form grid" onSubmit={savePerfil}>
      <label>Nombre completo<input value={perfil.nombre_completo || ''} onChange={e => setPerfil({ ...perfil, nombre_completo: e.target.value })} /></label>
      <label>Email<input value={perfil.email || ''} onChange={e => setPerfil({ ...perfil, email: e.target.value })} /></label>
      <label>Teléfono<input value={perfil.telefono || ''} onChange={e => setPerfil({ ...perfil, telefono: e.target.value })} /></label>
      <label>Profesión<input value={perfil.profesion || ''} onChange={e => setPerfil({ ...perfil, profesion: e.target.value })} /></label>
      <label>Años experiencia<select value={perfil.experiencia_anios || ''} onChange={e => setPerfil({ ...perfil, experiencia_anios: e.target.value })}>
        <option value="">Seleccionar...</option>
        <option value="0">0 años</option>
        <option value="1">1 año</option>
        <option value="2">2 años</option>
        <option value="3">3 años</option>
        <option value="4">4 años</option>
        <option value="5+">5 o más años</option>
      </select></label>
      <label>CV / URL<input value={perfil.cv || ''} onChange={e => setPerfil({ ...perfil, cv: e.target.value })} /></label>
      <label>Foto perfil / URL<input value={perfil.foto_perfil || ''} onChange={e => setPerfil({ ...perfil, foto_perfil: e.target.value })} /></label>
      <button className="primary">Guardar perfil</button>
    </form>}
    <h3>Vacantes disponibles</h3>
    <div className="cards">{vacantes.map(v => {
      const postulada = vacantePostulada(v.id_vacante)
      return <div className="card" key={v.id_vacante}>
        <h3>{v.titulo}</h3>
        <p>{v.descripcion}</p>
        <small>{v.departamento} · ${Number(v.salario_minimo).toLocaleString()} - ${Number(v.salario_maximo).toLocaleString()}</small>
        <button disabled={postulada} onClick={() => postular(v.id_vacante)} style={{background: postulada ? '#ccc' : '', cursor: postulada ? 'not-allowed' : 'pointer'}}>
          {postulada ? '✓ Ya postulaste' : 'Postular'}
        </button>
      </div>
    })}</div>
  </section>
}

function VacantesTable({ vacantes, onCerrar }) {
  return <div className="card"><table><thead><tr><th>ID</th><th>Título</th><th>Departamento</th><th>Estado</th><th>Acción</th></tr></thead><tbody>{vacantes.map(v => <tr key={v.id_vacante}><td>{v.id_vacante}</td><td>{v.titulo}</td><td>{v.departamento}</td><td><Badge>{v.estado}</Badge></td><td>{v.estado === 'abierta' && <button onClick={() => onCerrar(v.id_vacante)}>Cerrar</button>}</td></tr>)}</tbody></table></div>
}

function Postulaciones({ mine }) {
  const user = getUser()
  const [items, setItems] = useState([])
  const [evaluaciones, setEvaluaciones] = useState({})
  const [error, setError] = useState('')
  const [expandido, setExpandido] = useState(null)

  async function load() { 
    const postulaciones = await api('/postulaciones/')
    setItems(postulaciones)
    if (mine) {
      const evals = await api('/evaluaciones/')
      const evalMap = {}
      evals.forEach(e => {
        evalMap[e.id_postulacion] = e
      })
      setEvaluaciones(evalMap)
    }
  }
  useEffect(() => { load().catch(e => setError(e.message)) }, [])

  async function change(id, estado) {
    await api(`/postulaciones/${id}/estado/`, { method: 'POST', body: JSON.stringify({ estado }) })
    await load()
  }

  return <section>
    <Header title={mine ? "Mis Postulaciones" : "Postulaciones"} subtitle={mine ? "Seguimiento de tus candidaturas y evaluaciones." : "Seguimiento del estado de candidatos."} />
    {error && <div className="error">{error}</div>}
    <div className="card">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Candidato</th>
            <th>Vacante</th>
            <th>Estado</th>
            <th>Fecha</th>
            {mine && <th>Evaluación</th>}
            {!mine && <th>Cambiar estado</th>}
          </tr>
        </thead>
        <tbody>
          {items.map(p => (
            <React.Fragment key={p.id_postulacion}>
              <tr>
                <td>{p.id_postulacion}</td>
                <td>{p.candidato_nombre}</td>
                <td>{p.vacante_titulo}</td>
                <td><Badge>{p.estado}</Badge></td>
                <td>{p.fecha_postulacion?.slice(0,10)}</td>
                {mine && <td>
                  {evaluaciones[p.id_postulacion] ? (
                    <button onClick={() => setExpandido(expandido === p.id_postulacion ? null : p.id_postulacion)} style={{background: 'none', border: 'none', cursor: 'pointer', color: '#3b82f6', textDecoration: 'underline'}}>
                      Ver evaluación
                    </button>
                  ) : (
                    <span style={{color: '#999', fontSize: '0.9em'}}>Sin evaluar</span>
                  )}
                </td>}
                {!mine && <td><select value={p.estado} onChange={e => change(p.id_postulacion, e.target.value)}>{ESTADOS.map(s => <option key={s} value={s}>{s}</option>)}</select></td>}
              </tr>
              {mine && expandido === p.id_postulacion && evaluaciones[p.id_postulacion] && (
                <tr style={{background: '#f9fafb'}}>
                  <td colSpan="6" style={{padding: '20px'}}>
                    <div style={{borderLeft: '4px solid #3b82f6', paddingLeft: '15px'}}>
                      <h4 style={{margin: '0 0 10px 0', color: '#1f2937'}}>Evaluación</h4>
                      <p style={{margin: '5px 0'}}><strong>Calificación:</strong> {evaluaciones[p.id_postulacion].calificacion}/5</p>
                      <p style={{margin: '5px 0'}}><strong>Evaluador:</strong> {evaluaciones[p.id_postulacion].evaluador_nombre || 'Sin información'}</p>
                      <p style={{margin: '5px 0', whiteSpace: 'pre-wrap'}}><strong>Comentarios:</strong><br />{evaluaciones[p.id_postulacion].comentarios}</p>
                    </div>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </div>
  </section>
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
  
  async function deleteUsuario(id, nombre) {
    alert(`¿Está seguro que desea eliminar al usuario "${nombre}"?`)
    if (!confirm('Esta acción es irreversible. ¿Desea continuar?')) return
    try {
      await api(`/usuarios/${id}/delete/`, { method: 'DELETE' })
      await load()
    } catch (e) {
      setError(e.message)
    }
  }

  return <section><Header title="Panel Administración" subtitle="Gestión simple de usuarios y roles." />{error && <div className="error">{error}</div>}<form className="card form grid" onSubmit={submit}><label>Nombre<input value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} required /></label><label>Correo<input type="email" value={form.correo} onChange={e => setForm({ ...form, correo: e.target.value })} required /></label><label>Rol<select value={form.rol} onChange={e => setForm({ ...form, rol: e.target.value })}><option value="admin">admin</option><option value="analista">analista</option><option value="jefe_area">jefe_area</option><option value="candidato">candidato</option></select></label><label>Contraseña<input value={form.contrasena} onChange={e => setForm({ ...form, contrasena: e.target.value })} /></label><button className="primary">Crear usuario</button></form><div className="card"><table><thead><tr><th>ID</th><th>Nombre</th><th>Correo</th><th>Rol</th><th>Estado</th><th></th></tr></thead><tbody>{usuarios.map(u => <tr key={u.id_usuario}><td>{u.id_usuario}</td><td>{u.nombre}</td><td>{u.correo}</td><td>{u.rol}</td><td><Badge>{u.estado}</Badge></td><td><button className="danger" style={{padding: '4px 8px', background: 'none', border: 'none', cursor: 'pointer', color: '#ef4444'}} onClick={() => deleteUsuario(u.id_usuario, u.nombre)} title="Eliminar usuario"><X size={18} /></button></td></tr>)}</tbody></table></div></section>
}

function Historial() {
  const [filters, setFilters] = useState({id_postulacion: '', tipo: '', q: ''})
  const [items, setItems] = useState([])
  const [stats, setStats] = useState({total: 0, por_tipo: {}})
  const [error, setError] = useState('')
  const [expandedId, setExpandedId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  
  const loadData = async (searchFilters = {}) => {
    try {
      setLoading(true)
      setError('')
      const params = new URLSearchParams()
      if (searchFilters.id_postulacion) params.append('id_postulacion', searchFilters.id_postulacion)
      if (searchFilters.tipo) params.append('tipo', searchFilters.tipo)
      if (searchFilters.q) params.append('q', searchFilters.q)
      
      const url = params.toString() ? `/historial?${params}` : `/historial`
      const data = await api(url)
      setItems(data || [])
      
      // Calcular estadísticas
      const total = (data || []).length
      const por_tipo = {}
      data?.forEach(h => {
        por_tipo[h.tipo] = (por_tipo[h.tipo] || 0) + 1
      })
      setStats({total, por_tipo})
    } catch (e) {
      setError(e.message || 'Error al cargar historial')
    } finally {
      setLoading(false)
    }
  }
  
  // Carga inicial
  useEffect(() => {
    loadData()
  }, [])
  
  const handleFilter = (key, value) => {
    setFilters(prev => ({...prev, [key]: value}))
  }
  
  const handleSearch = () => {
    loadData(filters)
  }
  
  const handleReset = () => {
    setFilters({id_postulacion: '', tipo: '', q: ''})
    setExpandedId(null)
    loadData()
  }
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }
  
  const tiposUnicos = [...new Set(items.map(h => h.tipo))]
  const isFiltered = filters.id_postulacion || filters.tipo || filters.q
  
  return (
    <section>
      <Header title="Historial" subtitle="Trazabilidad completa de eventos del proceso." />
      {error && <div className="error">{error}</div>}
      
      {/* Barra de búsqueda principal */}
      <div className="toolbar" style={{gap: '8px'}}>
        <input 
          placeholder="Buscar: descripción, usuario, candidato, vacante..." 
          value={filters.q}
          onChange={e => handleFilter('q', e.target.value)}
          onKeyPress={handleKeyPress}
          style={{flex: 1}}
        />
        <button onClick={handleSearch} disabled={loading} style={{padding: '8px 20px'}}>
          {loading ? 'Buscando...' : 'Buscar'}
        </button>
        <button onClick={() => setShowFilters(!showFilters)} style={{padding: '8px 16px', background: showFilters ? '#007bff' : '#6c757d'}}>
          Filtros {isFiltered && <span style={{marginLeft: '4px', fontWeight: 'bold'}}>({Object.values(filters).filter(Boolean).length})</span>}
        </button>
      </div>
      
      {/* Filtros opcionales */}
      {showFilters && (
        <div className="card" style={{marginBottom: '12px', padding: '12px', background: '#f8f9fa', borderRadius: '4px'}}>
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px'}}>
            <div>
              <label style={{display: 'block', fontSize: '12px', fontWeight: 'bold', marginBottom: '4px'}}>ID Postulación</label>
              <input 
                placeholder="Ej: 1, 5, 10" 
                value={filters.id_postulacion}
                onChange={e => handleFilter('id_postulacion', e.target.value)}
                onKeyPress={handleKeyPress}
                style={{width: '100%', padding: '6px', fontSize: '12px'}}
              />
            </div>
            <div>
              <label style={{display: 'block', fontSize: '12px', fontWeight: 'bold', marginBottom: '4px'}}>Tipo de Evento</label>
              <select 
                value={filters.tipo}
                onChange={e => handleFilter('tipo', e.target.value)}
                style={{width: '100%', padding: '6px', fontSize: '12px'}}
              >
                <option value="">Todos los tipos</option>
                {tiposUnicos.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div style={{display: 'flex', alignItems: 'flex-end', gap: '6px'}}>
              <button onClick={handleReset} style={{flex: 1, padding: '6px', fontSize: '12px'}}>Limpiar filtros</button>
              <button onClick={handleSearch} style={{flex: 1, padding: '6px', fontSize: '12px', background: '#28a745', color: 'white'}}>Aplicar</button>
            </div>
          </div>
        </div>
      )}
      
      {/* Estadísticas */}
      {items.length > 0 && (
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '8px', marginBottom: '12px'}}>
          <div style={{padding: '8px', background: '#e7f3ff', borderRadius: '4px', textAlign: 'center'}}>
            <div style={{fontSize: '12px', color: '#666'}}>Total registros</div>
            <div style={{fontSize: '18px', fontWeight: 'bold', color: '#007bff'}}>{stats.total}</div>
          </div>
          {Object.entries(stats.por_tipo).map(([tipo, count]) => (
            <div key={tipo} style={{padding: '8px', background: '#f0f0f0', borderRadius: '4px', textAlign: 'center'}}>
              <div style={{fontSize: '11px', color: '#666'}}>{tipo}</div>
              <div style={{fontSize: '16px', fontWeight: 'bold'}}>{count}</div>
            </div>
          ))}
        </div>
      )}
      
      {/* Tabla de resultados */}
      <div className="card">
        {items.length === 0 ? (
          <div style={{padding: '24px', textAlign: 'center', color: '#999'}}>
            {loading ? 'Cargando...' : isFiltered ? 'No se encontraron registros' : 'Sin registros'}
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Postulación</th>
                <th>Tipo</th>
                <th>Descripción</th>
                <th>Usuario</th>
                <th>Entidad</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {items.map(h => (
                <React.Fragment key={h.id_historial}>
                  <tr style={{cursor: 'pointer', backgroundColor: h.is_deleted ? '#ffebee' : 'inherit', borderLeft: '3px solid ' + (h.tipo === 'cambio_campo' ? '#ff9800' : '#2196F3')}}>
                    <td>{h.fecha?.slice(0, 16).replace('T', ' ')}</td>
                    <td><strong>#{h.id_postulacion}</strong></td>
                    <td><Badge>{h.tipo}</Badge></td>
                    <td style={{maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis'}}>{h.descripcion}</td>
                    <td><small>{h.usuario_nombre}</small></td>
                    <td><small>{h.id_entidad_tipo || '-'}</small></td>
                    <td>
                      <button onClick={() => setExpandedId(expandedId === h.id_historial ? null : h.id_historial)} style={{padding: '4px 8px', cursor: 'pointer', background: 'none', border: 'none', fontSize: '14px'}}>
                        {expandedId === h.id_historial ? '▼' : '▶'}
                      </button>
                    </td>
                  </tr>
                  {expandedId === h.id_historial && (
                    <tr>
                      <td colSpan="7">
                        <div style={{padding: '16px', backgroundColor: '#f9f9f9', borderRadius: '4px', fontSize: '13px', lineHeight: '1.6'}}>
                          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px'}}>
                            <div>
                              <div style={{marginBottom: '12px'}}>
                                <strong>Información del evento</strong>
                                <div style={{marginTop: '8px', fontSize: '12px'}}>
                                  <div><strong>ID Historial:</strong> {h.id_historial}</div>
                                  <div><strong>Fecha:</strong> {h.fecha}</div>
                                  <div><strong>Usuario:</strong> {h.usuario_nombre || h.id_usuario}</div>
                                  <div><strong>Tipo:</strong> {h.tipo}</div>
                                </div>
                              </div>
                              <div>
                                <strong>Entidad auditada</strong>
                                <div style={{marginTop: '8px', fontSize: '12px', background: '#fff', padding: '8px', borderRadius: '2px'}}>
                                  <div><strong>Tipo:</strong> {h.id_entidad_tipo || 'N/A'}</div>
                                  <div><strong>ID:</strong> {h.id_entidad_referencia || 'N/A'}</div>
                                </div>
                              </div>
                            </div>
                            <div>
                              <div>
                                <strong>Descripción completa</strong>
                                <div style={{marginTop: '8px', fontSize: '12px', background: '#fff', padding: '8px', borderRadius: '2px', maxHeight: '120px', overflow: 'auto'}}>
                                  {h.descripcion}
                                </div>
                              </div>
                              {h.cambios_detalles && Object.keys(h.cambios_detalles).length > 0 && (
                                <div style={{marginTop: '12px'}}>
                                  <strong>Cambios detectados</strong>
                                  <pre style={{margin: '8px 0', padding: '8px', backgroundColor: '#f0f0f0', borderRadius: '2px', overflow: 'auto', fontSize: '11px', maxHeight: '100px'}}>
                                    {JSON.stringify(h.cambios_detalles, null, 2)}
                                  </pre>
                                </div>
                              )}
                              {h.is_deleted && (
                                <div style={{marginTop: '8px', padding: '8px', backgroundColor: '#ffebee', borderRadius: '2px', color: '#c62828', fontSize: '12px'}}>
                                  <strong>MARCADO COMO ELIMINADO</strong>
                                  <div>{h.fecha_eliminacion?.slice(0, 16).replace('T', ' ')}</div>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  )
}

function Header({ title, subtitle }) { return <div className="header"><h1>{title}</h1><p>{subtitle}</p></div> }
function Badge({ children }) { return <span className="badge">{children}</span> }

export default App
