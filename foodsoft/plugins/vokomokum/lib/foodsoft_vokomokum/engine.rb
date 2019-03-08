module FoodsoftVokomokum
  class Engine < ::Rails::Engine
    def navigation(primary, ctx)
      # Remove tasks and ordergroup menu items
      if item = primary[:foodcoop]
        if menu = item.sub_navigation
          menu.items.delete(menu[:ordergroups])
          menu.items.delete(menu[:tasks])
        end
      end
    end
  end
end
