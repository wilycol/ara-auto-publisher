import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { campaignsApi } from '../api/campaigns';
import { postsApi } from '../api/posts';
import { identitiesApi } from '../api/identities';
import type { Identity } from '../api/identities';
import type { Campaign, Post } from '../types';
import { ArrowLeft, Calendar, Target, FileText, Share2, AlertCircle, Edit, Wand2, X, Check, Copy, Rocket } from 'lucide-react';

export const CampaignDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [identities, setIdentities] = useState<Identity[]>([]);

  // Edit Campaign Mode State
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState<Partial<Campaign>>({});

  // Edit Post Mode State
  const [editingPostId, setEditingPostId] = useState<number | null>(null);
  const [editPostForm, setEditPostForm] = useState<{
    title: string;
    content: string;
    date: string;
  }>({ title: '', content: '', date: '' });

  useEffect(() => {
    if (id) {
      loadCampaign(parseInt(id));
      loadIdentities();
    }
  }, [id]);

  const loadIdentities = async () => {
    try {
      const data = await identitiesApi.getAll();
      setIdentities(data);
    } catch (err) {
      console.error('Error loading identities', err);
    }
  };

  const loadCampaign = async (campaignId: number) => {
    try {
      setLoading(true);
      const data = await campaignsApi.getOne(campaignId);
      setCampaign(data);
      // Initialize edit form
      setEditForm({
        name: data.name,
        objective: data.objective,
        tone: data.tone,
        start_date: data.start_date,
        end_date: data.end_date
      });
    } catch (err) {
      console.error('Error loading campaign details', err);
      setError('No se pudo cargar la campaña. Intenta nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateContent = async () => {
    if (!campaign) return;
    try {
      setGenerating(true);
      const result = await campaignsApi.generatePosts(campaign.id, 3, 'linkedin'); // Default to 3 posts
      
      if (result.generated_count === 0) {
        setError('La IA no pudo generar posts. Verifica la configuración o intenta de nuevo.');
      } else {
        // Reload campaign to show new posts
        await loadCampaign(campaign.id);
        setError(null); // Clear any previous error
      }
    } catch (err) {
      console.error('Error generating content', err);
      setError('Error generando contenido. Intenta de nuevo.');
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!campaign) return;
    try {
      const updated = await campaignsApi.update(campaign.id, editForm);
      setCampaign(updated);
      setIsEditing(false);
    } catch (err) {
      console.error('Error updating campaign', err);
      setError('Error guardando cambios.');
    }
  };

  const handleCopyToClipboard = () => {
    if (!campaign?.posts) return;
    const allContent = campaign.posts.map(p => `--- POST ---\n${p.content_text || p.content}\n`).join('\n');
    navigator.clipboard.writeText(allContent);
    alert('Contenido copiado al portapapeles');
  };

  // Post Actions
  const handleEditPost = (post: Post) => {
    setEditingPostId(post.id);
    const dateVal = post.scheduled_for || post.scheduled_date;
    setEditPostForm({
      title: post.title || '',
      content: post.content_text || post.content || '',
      date: dateVal ? dateVal.split('T')[0] : ''
    });
  };

  const handleCancelPostEdit = () => {
    setEditingPostId(null);
    setEditPostForm({ title: '', content: '', date: '' });
  };

  const handleSavePost = async (postId: number) => {
    try {
      await postsApi.update(postId, {
        title: editPostForm.title,
        content_text: editPostForm.content,
        scheduled_for: editPostForm.date // Use scheduled_for directly
      });
      // Refresh campaign to show updates
      if (campaign) await loadCampaign(campaign.id);
      setEditingPostId(null);
    } catch (err) {
      console.error('Error updating post', err);
      alert('Error al guardar el post');
    }
  };

  const handleApprovePost = async (post: Post) => {
    // Validation: Date is required for approval
    const hasDate = post.scheduled_for || post.scheduled_date;
    
    if (!hasDate) {
        // If editing this post, check form date
        if (editingPostId === post.id && editPostForm.date) {
             alert("Primero debes GUARDAR la fecha antes de aprobar.");
             return;
        }
        alert("Para aprobar un post, primero debes asignarle una fecha. Edita el post y selecciona una fecha.");
        return;
    }

    try {
      await postsApi.update(post.id, { status: 'APPROVED' });
      if (campaign) await loadCampaign(campaign.id);
    } catch (err) {
      console.error('Error approving post', err);
      alert('Error al aprobar el post. Asegúrate de que tenga fecha asignada.');
    }
  };

  const handlePublishPost = async (post: Post) => {
    if (!confirm("¿Estás seguro de que quieres publicar este post ahora en LinkedIn?")) return;
    
    try {
        await postsApi.publishNow(post.id);
        alert("¡Post publicado exitosamente!");
        if (campaign) await loadCampaign(campaign.id);
    } catch (err: any) {
        console.error('Error publishing post', err);
        const msg = err.response?.data?.detail || 'Error al publicar el post.';
        alert(msg);
    }
  };

  const handleMarkAsPublished = async (post: Post) => {
    if (!confirm("¿Confirmas que ya has publicado este post manualmente? Se marcará como COMPLETADO.")) return;
    
    try {
        await postsApi.markAsPublished(post.id);
        if (campaign) await loadCampaign(campaign.id);
    } catch (err: any) {
        console.error('Error marking post as published', err);
        const msg = err.response?.data?.detail || 'Error al actualizar el post.';
        alert(msg);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';
      case 'DRAFT': return 'bg-slate-800 text-slate-400 border border-slate-700';
      case 'PAUSED': return 'bg-amber-500/10 text-amber-400 border border-amber-500/20';
      case 'COMPLETED': return 'bg-blue-500/10 text-blue-400 border border-blue-500/20';
      default: return 'bg-slate-800 text-slate-400 border border-slate-700';
    }
  };

  const getPostStatusColor = (status: string) => {
    switch (status) {
      case 'PUBLISHED': 
      case 'PUBLISHED_AUTO': return 'bg-emerald-500/10 text-emerald-400';
      case 'SCHEDULED': 
      case 'SCHEDULED_AUTO': return 'bg-blue-500/10 text-blue-400';
      case 'FAILED': 
      case 'FAILED_AUTO_MANUAL_AVAILABLE': return 'bg-red-500/10 text-red-400';
      case 'READY_MANUAL': return 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse';
      case 'GENERATED': return 'bg-purple-500/10 text-purple-400';
      case 'APPROVED': return 'bg-cyan-500/10 text-cyan-400';
      default: return 'bg-slate-700 text-slate-400';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500"></div>
      </div>
    );
  }

  if (error || !campaign) {
    return (
      <div className="text-center py-12">
        <div className="bg-red-500/10 text-red-400 p-4 rounded-lg inline-flex items-center gap-2 mb-4">
          <AlertCircle size={20} />
          {error || 'Campaña no encontrada'}
        </div>
        <br />
        <button 
          onClick={() => navigate('/campaigns')}
          className="text-slate-400 hover:text-white transition-colors flex items-center gap-2 mx-auto"
        >
          <ArrowLeft size={16} /> Volver a Campañas
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col gap-4">
        <button 
          onClick={() => navigate('/campaigns')}
          className="text-slate-400 hover:text-white transition-colors flex items-center gap-2 w-fit"
        >
          <ArrowLeft size={16} /> Volver
        </button>

        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-6">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              {isEditing ? (
                <input 
                  type="text" 
                  value={editForm.name} 
                  onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                  className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-2xl font-bold text-white w-full"
                />
              ) : (
                <h1 className="text-3xl font-bold text-white">{campaign.name}</h1>
              )}
              <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getStatusColor(campaign.status)}`}>
                {campaign.status}
              </span>
            </div>
            
            <div className="flex items-center gap-4 text-slate-400 text-sm">
              <span className="flex items-center gap-1">
                <Calendar size={14} /> 
                {isEditing ? (
                  <div className="flex gap-2 items-center">
                    <input 
                      type="date" 
                      value={editForm.start_date?.split('T')[0]} 
                      onChange={(e) => setEditForm({...editForm, start_date: e.target.value})}
                      className="bg-slate-800 border border-slate-700 rounded px-2 py-0.5 text-xs text-white"
                    />
                    <span>-</span>
                    <input 
                      type="date" 
                      value={editForm.end_date?.split('T')[0] || ''} 
                      onChange={(e) => setEditForm({...editForm, end_date: e.target.value})}
                      className="bg-slate-800 border border-slate-700 rounded px-2 py-0.5 text-xs text-white"
                    />
                  </div>
                ) : (
                  <>Inicio: {new Date(campaign.start_date).toLocaleDateString()}</>
                )}
              </span>
              <span className="text-slate-600">|</span>
              <span className="flex items-center gap-1">
                <FileText size={14} />
                {campaign.posts?.length || 0} Posts generados
              </span>
            </div>
          </div>
          
          <div className="flex gap-2">
            {isEditing ? (
              <>
                <button 
                  onClick={() => setIsEditing(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors text-sm font-medium flex items-center gap-2"
                >
                  <X size={16} /> Cancelar
                </button>
                <button 
                  onClick={handleSaveEdit}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition-colors text-sm font-medium flex items-center gap-2"
                >
                  <Check size={16} /> Guardar
                </button>
              </>
            ) : (
              <button 
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors text-sm font-medium flex items-center gap-2"
              >
                <Edit size={16} /> Editar Configuración
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Campaign Strategy Details */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="col-span-1 space-y-6">
          <div className="bg-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-800 p-6">
            <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
              <Target className="text-amber-500" size={20} />
              Estrategia
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="text-xs text-slate-500 uppercase tracking-wider block mb-1">Identidad</label>
                {isEditing ? (
                   <select 
                     value={editForm.identity_id || ''}
                     onChange={(e) => setEditForm({...editForm, identity_id: e.target.value})}
                     className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-slate-300 text-sm"
                   >
                     <option value="">-- Por defecto (Ara) --</option>
                     {identities.map(id => (
                       <option key={id.id} value={id.id}>{id.name}</option>
                     ))}
                   </select>
                ) : (
                   <p className="text-slate-300 font-medium">
                     {identities.find(i => i.id === campaign.identity_id)?.name || 'Ara (Por defecto)'}
                   </p>
                )}
              </div>

              <div>
                <label className="text-xs text-slate-500 uppercase tracking-wider block mb-1">Objetivo</label>
                {isEditing ? (
                  <textarea 
                    value={editForm.objective}
                    onChange={(e) => setEditForm({...editForm, objective: e.target.value})}
                    className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-slate-300 text-sm h-20"
                  />
                ) : (
                  <p className="text-slate-300">{campaign.objective || 'No definido'}</p>
                )}
              </div>
              
              <div>
                <label className="text-xs text-slate-500 uppercase tracking-wider block mb-1">Tono de Voz</label>
                {isEditing ? (
                  <input 
                    type="text"
                    value={editForm.tone}
                    onChange={(e) => setEditForm({...editForm, tone: e.target.value})}
                    className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-slate-300 text-sm"
                  />
                ) : (
                  <p className="text-slate-300">{campaign.tone || 'Estándar'}</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Posts List */}
        <div className="col-span-1 md:col-span-2">
          <div className="bg-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-800 p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-medium text-white flex items-center gap-2">
                <Share2 className="text-blue-500" size={20} />
                Contenido Generado
              </h3>
              
              {campaign.posts && campaign.posts.length > 0 && (
                <button 
                  onClick={handleCopyToClipboard}
                  className="text-slate-400 hover:text-white text-xs flex items-center gap-1 hover:bg-slate-800 px-2 py-1 rounded transition-colors"
                >
                  <Copy size={14} /> Copiar todo
                </button>
              )}
            </div>

            {!campaign.posts || campaign.posts.length === 0 ? (
              <div className="text-center py-12 border-2 border-dashed border-slate-800 rounded-lg">
                <p className="text-slate-500 mb-4">No hay posts generados para esta campaña.</p>
                <button 
                  onClick={handleGenerateContent}
                  disabled={generating}
                  className="bg-gradient-to-r from-amber-500 to-orange-600 text-white px-6 py-3 rounded-lg hover:from-amber-400 hover:to-orange-500 transition-all shadow-lg shadow-amber-500/20 flex items-center gap-2 mx-auto disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {generating ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Generando...
                    </>
                  ) : (
                    <>
                      <Wand2 size={20} />
                      Generar Contenido con IA
                    </>
                  )}
                </button>
                <p className="text-xs text-slate-600 mt-2 max-w-xs mx-auto">
                  Usará el objetivo y temáticas definidos para crear 3 borradores iniciales.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {campaign.posts.map((post: Post) => (
                  <div key={post.id} className="bg-slate-800/30 rounded-lg border border-slate-800 p-4 hover:border-slate-700 transition-colors">
                    {editingPostId === post.id ? (
                      // EDIT MODE
                      <div className="space-y-3">
                        <div className="flex flex-col sm:flex-row justify-between gap-4">
                           <div className="flex-1">
                             <label className="text-xs text-slate-500 block mb-1">Título</label>
                             <input 
                               type="text"
                               value={editPostForm.title}
                               onChange={(e) => setEditPostForm({...editPostForm, title: e.target.value})}
                               className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-sm text-white"
                             />
                           </div>
                           <div className="sm:w-auto w-full">
                             <label className="text-xs text-slate-500 block mb-1">Fecha</label>
                             <input 
                               type="date"
                               value={editPostForm.date}
                               onChange={(e) => setEditPostForm({...editPostForm, date: e.target.value})}
                               className="w-full sm:w-auto bg-slate-900 border border-slate-700 rounded px-2 py-1 text-sm text-white"
                             />
                           </div>
                        </div>
                        
                        <div>
                          <label className="text-xs text-slate-500 block mb-1">Contenido</label>
                          <textarea 
                            value={editPostForm.content}
                            onChange={(e) => setEditPostForm({...editPostForm, content: e.target.value})}
                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-slate-300 font-mono h-32"
                          />
                        </div>

                        <div className="flex justify-end gap-2">
                           <button 
                             onClick={handleCancelPostEdit}
                             className="px-3 py-1 bg-slate-700 hover:bg-slate-600 text-white rounded text-xs"
                           >
                             Cancelar
                           </button>
                           <button 
                             onClick={() => handleSavePost(post.id)}
                             className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs flex items-center gap-1"
                           >
                             <Check size={12} /> Guardar
                           </button>
                        </div>
                      </div>
                    ) : (
                      // VIEW MODE
                      <>
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <span className={`inline-block px-2 py-0.5 text-xs font-medium rounded mb-2 ${getPostStatusColor(post.status)}`}>
                              {post.status}
                            </span>
                            <h4 className="text-white font-medium">{post.title || 'Sin título'}</h4>
                          </div>
                          <div className="text-xs text-slate-500">
                            {(post.scheduled_for || post.scheduled_date) ? new Date(post.scheduled_for || post.scheduled_date!).toLocaleDateString() : 'Sin fecha'}
                          </div>
                        </div>
                        
                        <div className="bg-slate-900/50 p-3 rounded text-sm text-slate-300 font-mono whitespace-pre-wrap mb-3 border border-slate-800/50">
                          {post.content_text || post.content}
                        </div>

                        <div className="flex justify-end gap-2 mt-2 flex-wrap">
                          <button 
                            onClick={() => handleEditPost(post)}
                            disabled={post.status === 'APPROVED' || post.status === 'PUBLISHED' || post.status === 'PUBLISHED_AUTO'}
                            className="text-xs text-slate-400 hover:text-white px-2 py-1 hover:bg-slate-800 rounded transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                          >
                            Editar
                          </button>
                          
                          {(post.status === 'GENERATED' || post.status === 'DRAFT') && (
                            <button 
                                onClick={() => handleApprovePost(post)}
                                className="text-xs text-amber-500 hover:text-amber-400 px-2 py-1 hover:bg-amber-500/10 rounded transition-colors border border-amber-500/20"
                            >
                                Aprobar
                            </button>
                          )}

                          {post.status === 'APPROVED' && (
                            <button 
                                onClick={() => handlePublishPost(post)}
                                className="text-xs text-white bg-blue-600 hover:bg-blue-500 px-3 py-1 rounded transition-colors shadow-lg shadow-blue-600/20 flex items-center gap-1"
                            >
                                <Rocket size={12} /> Publicar Ahora
                            </button>
                          )}

                          {/* Manual Publishing Action */}
                          {(post.status === 'READY_MANUAL' || post.status === 'FAILED_AUTO_MANUAL_AVAILABLE' || post.status === 'GENERATED' || post.status === 'APPROVED') && (
                             <button 
                                onClick={() => handleMarkAsPublished(post)}
                                className="text-xs text-slate-300 hover:text-white border border-slate-600 hover:border-slate-500 px-3 py-1 rounded transition-colors flex items-center gap-1 ml-2"
                                title="Marcar como publicado si ya lo hiciste manualmente"
                            >
                                <Check size={12} /> Ya lo publiqué
                            </button>
                          )}
                        </div>
                      </>
                    )}
                  </div>
                ))}
                
                <div className="pt-4 border-t border-slate-800 flex justify-center">
                   <button 
                    onClick={handleGenerateContent}
                    disabled={generating}
                    className="text-amber-500 hover:text-amber-400 text-sm flex items-center gap-2 hover:bg-slate-800/50 px-4 py-2 rounded transition-colors"
                   >
                     <Wand2 size={16} />
                     {generating ? 'Generando más...' : 'Generar más opciones'}
                   </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
