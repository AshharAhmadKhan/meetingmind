import { useState } from 'react';
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  useDroppable,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

// Column component
function KanbanColumn({ id, title, actions, color }) {
  const { setNodeRef } = useDroppable({
    id,
    data: { type: 'column', status: id }
  });

  const s = {
    column: {
      flex: 1,
      minWidth: '280px',
      backgroundColor: '#1a1a1a',
      borderRadius: '8px',
      padding: '16px',
      border: `2px solid ${color}`,
    },
    header: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '16px',
      paddingBottom: '12px',
      borderBottom: `2px solid ${color}`,
    },
    title: {
      fontSize: '16px',
      fontWeight: '600',
      color: '#fff',
    },
    count: {
      backgroundColor: color,
      color: '#000',
      padding: '4px 12px',
      borderRadius: '12px',
      fontSize: '14px',
      fontWeight: '600',
    },
    list: {
      minHeight: '200px',
      display: 'flex',
      flexDirection: 'column',
      gap: '12px',
    },
    empty: {
      textAlign: 'center',
      padding: '40px 20px',
      color: '#666',
      fontSize: '14px',
    }
  };

  return (
    <div style={s.column} ref={setNodeRef}>
      <div style={s.header}>
        <span style={s.title}>{title}</span>
        <span style={s.count}>{actions.length}</span>
      </div>
      <SortableContext items={actions.map(a => a.id)} strategy={verticalListSortingStrategy}>
        <div style={s.list}>
          {actions.length === 0 ? (
            <div style={s.empty}>No items</div>
          ) : (
            actions.map(action => (
              <ActionCard key={action.id} action={action} />
            ))
          )}
        </div>
      </SortableContext>
    </div>
  );
}

// Action card component with risk gradient
function ActionCard({ action }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: action.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  // Risk score gradient (0-100)
  const riskScore = action.riskScore || 0;
  const getRiskColor = (score) => {
    if (score >= 75) return '#f44336'; // Critical - red
    if (score >= 50) return '#ff9800'; // High - orange
    if (score >= 25) return '#ffc107'; // Medium - yellow
    return '#4caf50'; // Low - green
  };

  const riskColor = getRiskColor(riskScore);
  const riskGradient = `linear-gradient(90deg, ${riskColor}22 0%, ${riskColor}11 ${riskScore}%, transparent ${riskScore}%)`;

  const s = {
    card: {
      backgroundColor: '#2a2a2a',
      border: '1px solid #444',
      borderRadius: '6px',
      padding: '12px',
      cursor: isDragging ? 'grabbing' : 'grab',
      background: riskGradient,
      borderLeft: `4px solid ${riskColor}`,
    },
    task: {
      fontSize: '14px',
      color: '#fff',
      marginBottom: '8px',
      lineHeight: '1.4',
    },
    meta: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      fontSize: '12px',
      color: '#999',
      marginTop: '8px',
    },
    owner: {
      color: '#4a9eff',
      fontWeight: '500',
    },
    deadline: {
      color: '#ff6b6b',
    },
    risk: {
      display: 'inline-block',
      padding: '2px 8px',
      borderRadius: '4px',
      fontSize: '11px',
      fontWeight: '600',
      backgroundColor: riskColor + '33',
      color: riskColor,
      marginTop: '8px',
    },
    meeting: {
      fontSize: '11px',
      color: '#666',
      marginTop: '4px',
      fontStyle: 'italic',
    }
  };

  const formatDeadline = (deadline) => {
    if (!deadline) return null;
    try {
      const date = new Date(deadline);
      const now = new Date();
      const diffDays = Math.ceil((date - now) / (1000 * 60 * 60 * 24));
      
      if (diffDays < 0) return `${Math.abs(diffDays)}d overdue`;
      if (diffDays === 0) return 'Due today';
      if (diffDays === 1) return 'Due tomorrow';
      return `${diffDays}d left`;
    } catch {
      return deadline;
    }
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <div style={s.card}>
        <div style={s.task}>{action.task}</div>
        <div style={s.meta}>
          <span style={s.owner}>{action.owner || 'Unassigned'}</span>
          {action.deadline && (
            <span style={s.deadline}>{formatDeadline(action.deadline)}</span>
          )}
        </div>
        {action.riskScore > 0 && (
          <div style={s.risk}>
            Risk: {action.riskScore}/100
          </div>
        )}
        {action.meetingTitle && (
          <div style={s.meeting}>from: {action.meetingTitle}</div>
        )}
      </div>
    </div>
  );
}

// Main Kanban Board
export default function KanbanBoard({ actions, onStatusChange }) {
  const [activeId, setActiveId] = useState(null);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Derive status from completed field for backward compatibility
  const getStatus = (action) => {
    if (action.status) return action.status;
    return action.completed ? 'done' : 'todo';
  };

  // Group actions by status
  const columns = {
    todo: { title: 'To Do', color: '#e8c06a', actions: [] },
    in_progress: { title: 'In Progress', color: '#6a9ae8', actions: [] },
    blocked: { title: 'Blocked', color: '#e87a6a', actions: [] },
    done: { title: 'Done', color: '#c8f04a', actions: [] },
  };

  actions.forEach(action => {
    const status = getStatus(action);
    if (columns[status]) {
      columns[status].actions.push(action);
    }
  });

  const handleDragStart = (event) => {
    setActiveId(event.active.id);
  };

  const handleDragEnd = (event) => {
    const { active, over } = event;
    setActiveId(null);

    if (!over) return;

    const activeAction = actions.find(a => a.id === active.id);
    if (!activeAction) return;

    // Check if dropped over a column
    const targetStatus = over.data?.current?.status || over.id;
    const currentStatus = getStatus(activeAction);

    // Only update if status changed
    if (targetStatus && targetStatus !== currentStatus && columns[targetStatus]) {
      console.log(`Moving action ${activeAction.id} from ${currentStatus} to ${targetStatus}`);
      onStatusChange(activeAction.meetingId, activeAction.id, targetStatus);
    }
  };

  const s = {
    container: {
      display: 'flex',
      gap: '20px',
      overflowX: 'auto',
      padding: '20px 0',
    },
    '@media (max-width: 768px)': {
      container: {
        flexDirection: 'column',
      }
    }
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div style={s.container}>
        {Object.entries(columns).map(([status, { title, color, actions }]) => (
          <KanbanColumn
            key={status}
            id={status}
            title={title}
            actions={actions}
            color={color}
          />
        ))}
      </div>
      <DragOverlay>
        {activeId ? (
          <ActionCard action={actions.find(a => a.id === activeId)} />
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}
