query = """

select m.id,m.picking_id,m.product_qty,( case when m.product_id is null then svl.product_id else m.product_id end) as product_id,m.inventory_id ,svl.quantity,svl.unit_cost,svl.value,svl.id,
( case when svl.create_date is null then m.date else  svl.create_date end) as date
from stock_move m 
full outer join stock_valuation_layer svl on (svl.stock_move_id = m.id )
where ( ( m.product_id = %s and m.state = 'done' ) or svl.product_id = %s ) and ( m.company_id = %s or svl.company_id = %s) 
order by product_id,date

"""