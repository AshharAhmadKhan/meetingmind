import React, { useState, useMemo, useCallback } from 'react';
import {
  DndContext,
  DragOverlay,
  closestCenter,
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
      maxWidth: '350px',
      backgroundColor: '#1a1a1a',
      borderRadius: '8px',
      padding: '16px',
      border: `2px solid ${color}`,
      display: 'flex',
      flexDirection: 'column',
      height: '100%', // Fill parent height
    },
    header: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '16px',
      paddingBottom: '12px',
      borderBottom: `2px solid ${color}`,
      flexShrink: 0, // Don't shrink header
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
      flex: 1, // Take remaining space
      display: 'flex',
      flexDirection: 'column',
      gap: '12px',
      overflowY: 'auto', // Scroll only if needed
      overflowX: 'hidden',
      paddingRight: '4px', // Space for scrollbar
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

// Memoized Action card component - prevents unnecessary re-renders
const ActionCard = React.memo(function ActionCard({ action }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: action.id });

  const style = useMemo(() => ({
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }), [transform, transition, isDragging]);

  // Risk score gradient (0-100) - clamped and smooth
  const riskScore = Math.min(Math.max(action.riskScore || 0, 0), 100);
  
  const getRiskColor = useCallback((score) => {
    if (score >= 75) return '#f44336'; // Critical - red
    if (score >= 50) return '#ff9800'; // High - orange
    if (score >= 25) return '#ffc107'; // Medium - yellow
    return '#4caf50'; // Low - green
  }, []);

  const riskColor = getRiskColor(riskScore);
  
  // Improved gradient with smooth transition
  const riskGradient = useMemo(() => 
    `linear-gradient(90deg, ${riskColor}33 0%, ${riskColor}22 ${riskScore}%, transparent ${riskScore}%)`
  , [riskColor, riskScore]);

  // Memoized styles
  const cardStyles = useMemo(() => ({
    card: {
      backgroundColor: '#2a2a2a',
      border: '1px solid #444',
      borderRadius: '6px',
      padding: '12px',
      cursor: isDragging ? 'grabbing' : 'grab',
      background: riskGradient,
      borderLeft: `4px solid ${riskColor}`,
      transition: 'background 0.3s ease, border-color 0.3s ease',
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
  }), [isDragging, riskGradient, riskColor]);

  // Timezone-safe deadline calculation
  const formatDeadline = useCallback((deadline) => {
    if (!deadline) return null;
    try {
      const date = new Date(deadline);
      const now = new Date();
      
      // Normalize to start of day for accurate comparison
      const dateStart = new Date(date.getFullYear(), date.getMonth(), date.getDate());
      const nowStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      
      const diffDays = Math.round((dateStart - nowStart) / (1000 * 60 * 60 * 24));
      
      if (diffDays < 0) return `${Math.abs(diffDays)}d overdue`;
      if (diffDays === 0) return 'Due today';
      if (diffDays === 1) return 'Due tomorrow';
      return `${diffDays}d left`;
    } catch {
      return deadline;
    }
  }, []);

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <div style={cardStyles.card}>
        <div style={cardStyles.task}>{action.task}</div>
        <div style={cardStyles.meta}>
          <span style={cardStyles.owner}>{action.owner || 'Unassigned'}</span>
          {action.deadline && (
            <span style={cardStyles.deadline}>{formatDeadline(action.deadline)}</span>
          )}
        </div>
        {action.riskScore > 0 && (
          <div style={cardStyles.risk}>
            Risk: {action.riskScore}/100
          </div>
        )}
        {action.meetingTitle && (
          <div style={cardStyles.meeting}>from: {action.meetingTitle}</div>
        )}
      </div>
    </div>
  );
});

// Main Kanban Board
export default function KanbanBoard({ actions, onStatusChange }) {
  const [activeId, setActiveId] = useState(null);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // CRITICAL FIX #1: Memoize status derivation function
  const getStatus = useCallback((action) => {
    const validStatuses = ['todo', 'in_progress', 'blocked', 'done'];
    
    // Status field is authoritative - fail fast if invalid
    if (action.status) {
      if (!validStatuses.includes(action.status)) {
        console.error(`Invalid status "${action.status}" for action ${action.id}`);
        // Fallback to completed field
        return action.completed ? 'done' : 'todo';
      }
      return action.status;
    }
    
    // Fallback for legacy data without status field
    return action.completed ? 'done' : 'todo';
  }, []);

  // CRITICAL FIX #2: Memoize column grouping - only recompute when actions change
  const columns = useMemo(() => {
    const grouped = {
      todo: { title: 'To Do', color: '#e8c06a', actions: [] },
      in_progress: { title: 'In Progress', color: '#6a9ae8', actions: [] },
      blocked: { title: 'Blocked', color: '#e87a6a', actions: [] },
      done: { title: 'Done', color: '#c8f04a', actions: [] },
    };

    actions.forEach(action => {
      const status = getStatus(action);
      if (grouped[status]) {
        grouped[status].actions.push(action);
      }
    });

    return grouped;
  }, [actions, getStatus]);

  const handleDragStart = useCallback((event) => {
    setActiveId(event.active.id);
  }, []);

  // CRITICAL FIX #3: Support reordering within same column
  const handleDragEnd = useCallback((event) => {
    const { active, over } = event;
    setActiveId(null);

    if (!over || over.id === active.id) {
      return;
    }

    const activeAction = actions.find(a => a.id === active.id);
    if (!activeAction) {
      return;
    }

    // Check if we're reordering within the same column
    const activeIndex = actions.findIndex(a => a.id === active.id);
    const overIndex = actions.findIndex(a => a.id === over.id);

    if (activeIndex !== -1 && overIndex !== -1) {
      const activeStatus = getStatus(activeAction);
      const overAction = actions.find(a => a.id === over.id);
      const overStatus = overAction ? getStatus(overAction) : null;

      // Same column reordering
      if (overStatus && activeStatus === overStatus) {
        console.log(`Reordering within ${activeStatus} column`);
        // TODO: Implement onReorder callback for within-column reordering
        // For now, we skip this as backend doesn't support order field yet
        return;
      }
    }

    // Moving to different column
    const targetStatus = over.data?.current?.status || over.id;
    const currentStatus = getStatus(activeAction);

    if (targetStatus && targetStatus !== currentStatus && columns[targetStatus]) {
      console.log(`Moving action ${activeAction.id} from ${currentStatus} to ${targetStatus}`);
      onStatusChange(activeAction.meetingId, activeAction.id, targetStatus);
    }
  }, [actions, getStatus, columns, onStatusChange]);

  // Memoized container styles
  const containerStyles = useMemo(() => ({
    display: 'flex',
    gap: '20px',
    height: 'calc(100vh - 320px)',
    minHeight: '600px',
    padding: '20px 0',
  }), []);

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div style={containerStyles}>
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
